# PAP-242 — Extraction Logic Report

## Scope completed
Implemented source-aware extraction hardening for the scraper stack with:
- improved page readiness handling in the browser layer
- tighter Transfermarkt field extraction
- tighter FBref table targeting
- explicit extraction validation diagnostics
- no-silent-failure scrape outcomes

## Root cause confirmed
The broken extraction path came from four combined problems:
1. generic page waits did not prove target content was ready
2. Transfermarkt field extraction relied on brittle text assumptions
3. FBref table selection was too broad and mixed match-stat vs per-90 tables
4. parsed payloads had no explicit validation/diagnostic status, so empty results could look superficially successful

## What changed
### Browser readiness
- `app/scraping/browser.py`
- added source-aware ready-selector probing after `networkidle`
- logs selector-missing and challenge-detected conditions explicitly

### Transfermarkt extraction
- `app/scraping/parsers.py`
- improved inline labeled-value extraction
- cleaned title-derived player name
- tightened transfer-row detection to real season/club-like rows

### FBref extraction
- `app/scraping/fbref_parsers.py`
- narrowed player-match-stat table targeting
- excluded per-90 tables from standard stat extraction
- added challenge-page signal on match payload
- tightened per-90 metric extraction

### Validation
- `app/scraping/validation.py`
- added post-parse validation and extraction status classification

### Orchestration
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- payloads now include `diagnostics`
- partial/blocked outcomes are logged explicitly instead of silently succeeding

## Extraction status values
- `success_complete`
- `success_partial`
- `schema_invalid`
- `selector_missing`
- `challenge_page`

## Sample extracted records
### Transfermarkt profile sample
```json
{
  "source": "transfermarkt",
  "source_url": "https://example.com/player",
  "player_name": "Patrik Mercado",
  "preferred_name": "Patrik David Mercado",
  "position": "Attacking Midfield",
  "date_of_birth": "Jan 1, 2003",
  "nationality": "Ecuador",
  "current_club": "Independiente del Valle",
  "market_value": "€5.50m"
}
```

### Transfermarkt transfer sample
```json
{
  "season": "2023",
  "date": "Jan 1, 2023",
  "from_club": "IDV U20",
  "to_club": "Independiente del Valle",
  "market_value": "€1.00m",
  "fee": "-",
  "source_url": "https://example.com/player"
}
```

### FBref match sample
```json
{
  "source": "fbref",
  "source_url": "https://fbref.com/en/matches/abc/2025-2026/Match",
  "external_id": "en/matches/abc/2025-2026/Match",
  "competition": "Liga Pro",
  "season": "2025-2026",
  "match_date": "2026-04-20",
  "home_club": "Independiente del Valle",
  "away_club": "Barcelona SC",
  "home_score": 2,
  "away_score": 1,
  "venue": "Banco Guayaquil"
}
```

### FBref player match stat sample
```json
{
  "source": "fbref",
  "source_url": "https://fbref.com/en/matches/abc/2025-2026/Match",
  "table_id": "stats_standard",
  "player_name": "Patrik Mercado",
  "club_name": "Independiente del Valle",
  "minutes": 90,
  "goals": 1,
  "assists": 0,
  "yellow_cards": null,
  "red_cards": null,
  "shots": 3,
  "passes_completed": 24,
  "xg": 0.42,
  "xa": 0.05,
  "progressive_carries": 5,
  "progressive_passes": 4,
  "progressive_receptions": 7,
  "carries_into_final_third": null,
  "passes_into_final_third": null,
  "carries_into_penalty_area": null,
  "passes_into_penalty_area": null
}
```

### FBref per-90 sample
```json
{
  "source": "fbref",
  "source_url": "https://fbref.com/en/matches/abc/2025-2026/Match",
  "table_id": "stats_standard_per_90",
  "player_name": "Patrik Mercado",
  "club_name": "Independiente del Valle",
  "metrics": {
    "goals_per90": "1.00",
    "assists_per90": "0.00"
  }
}
```

### FBref challenge sample
```json
{
  "source": "fbref",
  "extraction_status": "challenge_page",
  "missing_required_fields": ["home_club", "away_club"],
  "record_counts": {
    "player_match_stats": 0,
    "player_per_90": 0
  }
}
```

## Field mapping to internal schema
### Transfermarkt -> Silver `players`
- `player_name` -> `players.player_name`
- `preferred_name` -> `players.preferred_name`
- `position` -> `players.position`
- `date_of_birth` -> `players.date_of_birth`
- `nationality` -> `players.nationality`
- `current_club` -> `players.current_club`
- `market_value` -> `players.market_value`

### Transfermarkt -> Silver `transfers`
- `season` -> `transfers.season`
- `date` -> `transfers.date`
- `from_club` -> `transfers.from_club`
- `to_club` -> `transfers.to_club`
- `market_value` -> `transfers.market_value`
- `fee` -> `transfers.fee`

### FBref -> Silver `matches`
- `external_id` -> `matches.external_id`
- `competition` -> `matches.competition`
- `season` -> `matches.season`
- `match_date` -> `matches.match_date`
- `home_club` -> `matches.home_club`
- `away_club` -> `matches.away_club`
- `home_score` -> `matches.home_score`
- `away_score` -> `matches.away_score`
- `venue` -> `matches.venue`

### FBref -> Silver `player_match_stats`
- `player_name` -> `player_match_stats.player_name`
- `club_name` -> `player_match_stats.club_name`
- `minutes` -> `player_match_stats.minutes`
- `goals` -> `player_match_stats.goals`
- `assists` -> `player_match_stats.assists`
- `yellow_cards` -> `player_match_stats.yellow_cards`
- `red_cards` -> `player_match_stats.red_cards`
- `shots` -> `player_match_stats.shots`
- `passes_completed` -> `player_match_stats.passes_completed`
- `xg` -> `player_match_stats.xg`
- `xa` -> `player_match_stats.xa`
- `progressive_carries` -> `player_match_stats.progressive_carries`
- `progressive_passes` -> `player_match_stats.progressive_passes`
- `progressive_receptions` -> `player_match_stats.progressive_receptions`
- `carries_into_final_third` -> `player_match_stats.carries_into_final_third`
- `passes_into_final_third` -> `player_match_stats.passes_into_final_third`
- `carries_into_penalty_area` -> `player_match_stats.carries_into_penalty_area`
- `passes_into_penalty_area` -> `player_match_stats.passes_into_penalty_area`

### FBref -> Silver `player_per90`
- `player_name` -> `player_per90.player_name`
- `club_name` -> `player_per90.club_name`
- `metrics` -> `player_per90.metrics`

## Validation outcome
- Transfermarkt fixture path now returns non-empty normalized records with `success_complete`
- FBref fixture path now returns non-empty normalized records with `success_complete`
- FBref challenge fixture is classified explicitly as `challenge_page`

## Notes
- live browser execution is still constrained by runtime Playwright availability and FBref anti-bot behavior
- this ticket fixes extraction logic and makes blocked/empty cases explicit; it does not claim that Cloudflare is bypassed in this environment
