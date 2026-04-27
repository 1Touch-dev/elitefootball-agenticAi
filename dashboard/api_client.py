from __future__ import annotations

import os
from typing import Any

import requests


DEFAULT_API_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT_SECONDS = 10


class DashboardAPIError(RuntimeError):
    """Raised when the dashboard cannot fetch valid data from the backend API."""


class DashboardAPIClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.base_url = (base_url or os.getenv("ELITEFOOTBALL_API_BASE_URL") or DEFAULT_API_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise DashboardAPIError(f"Unable to reach backend API at {url}: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise DashboardAPIError(f"Backend API returned invalid JSON for {url}") from exc

        if not isinstance(payload, dict):
            raise DashboardAPIError(f"Backend API returned an unexpected payload for {url}")
        return payload

    def get_health(self) -> dict[str, Any]:
        return self._get("/health")

    def get_dashboard_status(self) -> dict[str, Any]:
        return self._get("/dashboard/status")

    def get_players(
        self,
        *,
        name: str | None = None,
        position: str | None = None,
        club: str | None = None,
        include: str = "features,kpi,valuation",
        limit: int = 200,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._get(
            "/players",
            params={
                "name": name,
                "position": position,
                "club": club,
                "include": include,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_player_stats(self, player_name: str, *, limit: int = 20, offset: int = 0, sort: str = "-match_date") -> dict[str, Any]:
        return self._get(
            f"/players/{player_name}/stats",
            params={"limit": limit, "offset": offset, "sort": sort},
        )

    def get_compare(self, player_name: str, *, limit: int = 5) -> dict[str, Any]:
        return self._get("/compare", params={"player_name": player_name, "limit": limit})

    def get_value(
        self,
        *,
        player_name: str | None = None,
        tier: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._get(
            "/value",
            params={
                "player_name": player_name,
                "tier": tier,
                "limit": limit,
                "offset": offset,
            },
        )
