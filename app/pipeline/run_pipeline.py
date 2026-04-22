from __future__ import annotations

from app.analysis.advanced_metrics_engine import build_advanced_metrics_output
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables


def run_pipeline() -> dict[str, object]:
    bronze = build_bronze_manifest()
    silver = build_silver_tables()
    gold = build_gold_features(silver["tables"])
    advanced_metrics = build_advanced_metrics_output(silver["tables"])
    return {
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "advanced_metrics": advanced_metrics,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(result)
