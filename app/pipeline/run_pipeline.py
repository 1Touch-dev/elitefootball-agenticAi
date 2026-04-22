from __future__ import annotations

from app.analysis.kpi_engine import build_kpi_engine_output
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables


def run_pipeline() -> dict[str, object]:
    bronze = build_bronze_manifest()
    silver = build_silver_tables()
    gold = build_gold_features(silver["tables"])
    kpi = build_kpi_engine_output(silver["tables"])
    return {
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "kpi": kpi,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(result)
