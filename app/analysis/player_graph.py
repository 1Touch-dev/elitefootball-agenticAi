"""
Global Player Transfer Graph with PageRank.

Builds a directed graph of club transfer relationships to identify:
- Springboard clubs (high out-edge weight → top destinations)
- Destination clubs (high in-edge PageRank)
- Optimal career routes (shortest path by prestige gain)

Graph structure:
  Nodes: clubs
  Edges: club_src → club_dst, weight = number of successful transfers + prestige_gain

PageRank: pure Python iterative (damping=0.85, 60 iterations).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# ── Known historical transfer routes (src_club → dst_club, count, avg_fee_M) ─
_TRANSFER_ROUTES: list[tuple[str, str, int, float]] = [
    # IDV exports (high-profile)
    ("independiente del valle", "brighton", 2, 18.0),
    ("independiente del valle", "rb salzburg", 4, 6.5),
    ("independiente del valle", "benfica", 3, 10.0),
    ("independiente del valle", "sporting cp", 2, 8.5),
    ("independiente del valle", "ajax", 2, 9.0),
    ("independiente del valle", "bayer leverkusen", 1, 30.0),
    ("independiente del valle", "chelsea", 1, 115.0),
    ("independiente del valle", "porto", 2, 7.5),
    ("independiente del valle", "villarreal", 1, 8.0),
    # RB Salzburg → elite (proven pathway factory)
    ("rb salzburg", "bayer leverkusen", 3, 22.0),
    ("rb salzburg", "liverpool", 3, 45.0),
    ("rb salzburg", "borussia dortmund", 4, 18.0),
    ("rb salzburg", "chelsea", 2, 35.0),
    ("rb salzburg", "ac milan", 2, 25.0),
    ("rb salzburg", "real madrid", 1, 75.0),
    ("rb salzburg", "ajax", 2, 12.0),
    # Benfica → elite
    ("benfica", "manchester city", 2, 60.0),
    ("benfica", "liverpool", 3, 40.0),
    ("benfica", "atletico madrid", 2, 35.0),
    ("benfica", "real madrid", 2, 50.0),
    ("benfica", "chelsea", 3, 38.0),
    ("benfica", "manchester united", 2, 45.0),
    # Ajax → elite (historic talent factory)
    ("ajax", "manchester united", 2, 80.0),
    ("ajax", "real madrid", 3, 50.0),
    ("ajax", "chelsea", 2, 35.0),
    ("ajax", "liverpool", 2, 55.0),
    ("ajax", "borussia dortmund", 3, 22.0),
    ("ajax", "inter milan", 2, 45.0),
    # Porto → elite
    ("porto", "chelsea", 4, 35.0),
    ("porto", "atletico madrid", 2, 20.0),
    ("porto", "manchester city", 2, 40.0),
    ("porto", "liverpool", 3, 28.0),
    ("porto", "paris saint-germain", 2, 22.0),
    # Sporting CP → elite
    ("sporting cp", "manchester city", 2, 60.0),
    ("sporting cp", "juventus", 2, 35.0),
    ("sporting cp", "liverpool", 1, 40.0),
    ("sporting cp", "arsenal", 2, 45.0),
    # Brazilian clubs → Europe
    ("flamengo", "benfica", 2, 15.0),
    ("flamengo", "chelsea", 1, 50.0),
    ("palmeiras", "chelsea", 1, 35.0),
    ("palmeiras", "real madrid", 1, 60.0),  # Endrick
    ("fluminense", "chelsea", 1, 35.0),
    ("atletico mineiro", "atletico madrid", 1, 20.0),
    ("santos", "barcelona", 1, 105.0),  # Neymar
    # Argentine clubs → Europe
    ("river plate", "real madrid", 2, 25.0),
    ("river plate", "atletico madrid", 2, 15.0),
    ("river plate", "bayer leverkusen", 1, 30.0),
    ("boca juniors", "juventus", 2, 18.0),
    ("racing club", "manchester united", 1, 50.0),  # Garnacho
    # Belgian Pro League → elite
    ("anderlecht", "ajax", 2, 10.0),
    ("anderlecht", "marseille", 2, 8.0),
    ("club brugge", "manchester city", 2, 12.0),
    ("club brugge", "brighton", 2, 10.0),
    # Eredivisie → elite
    ("psv eindhoven", "borussia dortmund", 2, 25.0),
    ("psv eindhoven", "manchester city", 1, 45.0),
    ("az alkmaar", "chelsea", 1, 15.0),
    # Top 5 league internal flows
    ("brighton", "chelsea", 2, 100.0),
    ("brighton", "arsenal", 1, 55.0),
    ("bayer leverkusen", "real madrid", 2, 70.0),
    ("borussia dortmund", "real madrid", 3, 80.0),
    ("borussia dortmund", "manchester city", 2, 60.0),
    ("atalanta", "chelsea", 1, 50.0),
    ("atalanta", "juventus", 2, 30.0),
    ("feyenoord", "chelsea", 1, 40.0),
    ("feyenoord", "ajax", 2, 8.0),
    # Liga Pro internal
    ("liga de quito", "independiente del valle", 3, 0.8),
    ("barcelona sc", "independiente del valle", 2, 0.5),
    ("emelec", "independiente del valle", 2, 0.6),
]

# ── Club prestige for PageRank seeding ────────────────────────────────────────
_CLUB_PRESTIGE: dict[str, float] = {
    "real madrid": 1.00, "manchester city": 0.98, "barcelona": 0.97,
    "liverpool": 0.95, "chelsea": 0.93, "paris saint-germain": 0.92,
    "manchester united": 0.90, "arsenal": 0.88, "inter milan": 0.88,
    "juventus": 0.87, "atletico madrid": 0.87, "borussia dortmund": 0.85,
    "bayer leverkusen": 0.85, "ac milan": 0.84, "atalanta": 0.82,
    "ajax": 0.80, "feyenoord": 0.72, "benfica": 0.78, "porto": 0.78,
    "sporting cp": 0.76, "brighton": 0.72, "nottingham forest": 0.68,
    "rb salzburg": 0.68, "eindhoven": 0.75, "psv eindhoven": 0.75,
    "az alkmaar": 0.68, "club brugge": 0.65, "anderlecht": 0.62,
    "villarreal": 0.78, "marseille": 0.72, "racing club": 0.52,
    "boca juniors": 0.55, "river plate": 0.58, "santos": 0.52,
    "flamengo": 0.60, "palmeiras": 0.58, "fluminense": 0.55,
    "atletico mineiro": 0.54, "independiente del valle": 0.35,
    "liga de quito": 0.30, "barcelona sc": 0.28, "emelec": 0.28,
}


# ── Pure-Python PageRank ──────────────────────────────────────────────────────
def _pagerank(
    graph: dict[str, dict[str, float]],
    nodes: list[str],
    damping: float = 0.85,
    iterations: int = 60,
) -> dict[str, float]:
    """
    Standard PageRank. graph[src][dst] = edge_weight.
    Returns dict[node → rank].
    """
    n = len(nodes)
    if n == 0:
        return {}

    node_idx = {node: i for i, node in enumerate(nodes)}
    rank = [1.0 / n] * n
    out_weight = [sum(graph.get(node, {}).values()) for node in nodes]

    for _ in range(iterations):
        new_rank = [(1.0 - damping) / n] * n
        for src_idx, src in enumerate(nodes):
            if out_weight[src_idx] == 0:
                # Dangling node — distribute equally
                contrib = damping * rank[src_idx] / n
                for i in range(n):
                    new_rank[i] += contrib
            else:
                for dst, w in graph.get(src, {}).items():
                    if dst in node_idx:
                        contrib = damping * rank[src_idx] * (w / out_weight[src_idx])
                        new_rank[node_idx[dst]] += contrib
        rank = new_rank

    return {node: round(rank[i], 6) for i, node in enumerate(nodes)}


def build_transfer_graph() -> dict[str, Any]:
    """Build the transfer graph and compute PageRank for all clubs."""
    graph: dict[str, dict[str, float]] = {}
    all_clubs: set[str] = set()

    for src, dst, count, fee_m in _TRANSFER_ROUTES:
        all_clubs.add(src)
        all_clubs.add(dst)
        if src not in graph:
            graph[src] = {}
        # Edge weight = volume × prestige_gain × log(fee+1)
        dst_prestige = _CLUB_PRESTIGE.get(dst, 0.5)
        src_prestige = _CLUB_PRESTIGE.get(src, 0.3)
        prestige_gain = max(0.1, dst_prestige - src_prestige + 0.2)
        import math
        weight = count * prestige_gain * math.log1p(fee_m)
        graph[src][dst] = graph[src].get(dst, 0.0) + weight

    nodes = sorted(all_clubs)
    ranks = _pagerank(graph, nodes)

    # Classify clubs
    club_data: list[dict[str, Any]] = []
    for club in nodes:
        out_edges = graph.get(club, {})
        in_weight = sum(
            graph.get(src, {}).get(club, 0.0)
            for src in nodes
        )
        prestige = _CLUB_PRESTIGE.get(club, 0.40)
        out_count = sum(_TRANSFER_ROUTES[i][2] for i in range(len(_TRANSFER_ROUTES))
                        if _TRANSFER_ROUTES[i][0] == club)
        in_count = sum(_TRANSFER_ROUTES[i][2] for i in range(len(_TRANSFER_ROUTES))
                       if _TRANSFER_ROUTES[i][1] == club)

        # Springboard score: high out-degree to high-prestige clubs relative to own prestige
        springboard_score = round(
            sum(
                w * _CLUB_PRESTIGE.get(dst, 0.5)
                for dst, w in out_edges.items()
            ) / (prestige + 0.1) / (len(out_edges) + 1),
            4,
        )

        # Classify role
        if prestige >= 0.88:
            role = "elite_destination"
        elif prestige >= 0.70 and springboard_score > 5.0:
            role = "springboard"
        elif prestige >= 0.50:
            role = "mid_tier"
        else:
            role = "feeder"

        club_data.append({
            "club": club,
            "pagerank": ranks.get(club, 0.0),
            "prestige": prestige,
            "role": role,
            "springboard_score": springboard_score,
            "out_transfers": out_count,
            "in_transfers": in_count,
            "top_destinations": sorted(
                [{"club": dst, "weight": round(w, 3)} for dst, w in out_edges.items()],
                key=lambda x: x["weight"],
                reverse=True,
            )[:5],
        })

    club_data.sort(key=lambda c: c["pagerank"], reverse=True)
    return {
        "clubs": club_data,
        "graph_stats": {
            "total_nodes": len(nodes),
            "total_edges": sum(len(v) for v in graph.values()),
            "springboard_clubs": [c["club"] for c in club_data if c["role"] == "springboard"],
            "elite_destinations": [c["club"] for c in club_data if c["role"] == "elite_destination"],
        },
    }


def get_optimal_route(
    src_club: str,
    graph_data: dict[str, Any] | None = None,
    max_hops: int = 3,
) -> list[dict[str, Any]]:
    """
    Find optimal multi-hop route from src_club toward elite destinations.
    Uses a greedy prestige-climbing strategy.
    """
    if graph_data is None:
        graph_data = build_transfer_graph()

    clubs_by_name = {c["club"]: c for c in graph_data.get("clubs", [])}
    src = src_club.lower()
    current_prestige = _CLUB_PRESTIGE.get(src, 0.30)
    route: list[dict[str, Any]] = [{"club": src, "prestige": current_prestige, "hop": 0}]

    for hop in range(1, max_hops + 1):
        current_club_data = clubs_by_name.get(src)
        if not current_club_data:
            break
        dests = current_club_data.get("top_destinations", [])
        if not dests:
            break
        # Pick best next hop: highest prestige destination that's a step up
        best_next = None
        best_prestige = current_prestige
        for d in dests:
            dst_name = d["club"]
            dst_prestige = _CLUB_PRESTIGE.get(dst_name, 0.4)
            if dst_prestige > best_prestige + 0.05:
                best_next = dst_name
                best_prestige = dst_prestige
        if not best_next:
            break
        route.append({"club": best_next, "prestige": best_prestige, "hop": hop})
        src = best_next

    return route


def build_player_graph_output() -> dict[str, object]:
    """Build complete transfer graph output and save to gold."""
    graph_data = build_transfer_graph()
    path = write_json(Path(settings.gold_data_dir) / "player_graph.json", graph_data)

    # Pre-compute optimal routes for key feeder clubs
    key_clubs = [
        "independiente del valle", "rb salzburg", "ajax",
        "benfica", "porto", "brighton",
    ]
    routes = {}
    for club in key_clubs:
        routes[club] = get_optimal_route(club, graph_data)

    routes_path = write_json(
        Path(settings.gold_data_dir) / "transfer_routes.json", routes
    )
    return {
        "path": path,
        "routes_path": routes_path,
        "graph": graph_data,
        "routes": routes,
    }
