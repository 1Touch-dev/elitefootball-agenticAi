from __future__ import annotations
from app.pipeline.transfers import _parse_fee, build_silver_transfers, build_gold_transfer_features


def test_parse_fee_millions():
    assert _parse_fee("€5.2m") == 5_200_000.0


def test_parse_fee_thousands():
    assert _parse_fee("500k") == 500_000.0


def test_parse_fee_numeric():
    assert _parse_fee("12000000") == 12_000_000.0


def test_parse_fee_none():
    assert _parse_fee(None) is None


def test_parse_fee_invalid():
    assert _parse_fee("free") is None


def test_build_silver_transfers():
    raw = [{"player_name": "Test Player", "from_club": "Club A", "to_club": "Club B", "fee": "€1m", "season": "2023/24"}]
    silver = build_silver_transfers(raw)
    assert len(silver) == 1
    assert silver[0]["fee_eur"] == 1_000_000.0
    assert silver[0]["player_name"] == "Test Player"


def test_build_gold_features_resale():
    silver = [
        {"player_name": "Test Player", "from_club": "A", "to_club": "B", "fee_eur": 1_000_000.0, "season": "2021", "loan": False, "transfer_type": "transfer", "source": "tm"},
        {"player_name": "Test Player", "from_club": "B", "to_club": "C", "fee_eur": 4_000_000.0, "season": "2023", "loan": False, "transfer_type": "transfer", "source": "tm"},
    ]
    gold = build_gold_transfer_features(silver)
    assert len(gold) == 1
    assert gold[0]["resale_multiplier"] == 4.0
    assert gold[0]["total_transfers"] == 2
