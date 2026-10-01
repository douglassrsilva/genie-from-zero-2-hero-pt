from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "prepared"


def test_manifest_counts_and_hashes() -> None:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    expected = {
        "sites.parquet": 30,
        "assets.parquet": 120,
        "telemetry_5min.parquet": 241_920,
        "alarms.parquet": 480,
        "work_orders.parquet": 240,
        "operating_thresholds.parquet": 18,
    }
    actual = {entry["arquivo"]: entry["linhas"] for entry in manifest["arquivos"]}
    assert actual == expected
    for entry in manifest["arquivos"]:
        path = DATA / entry["arquivo"]
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_relational_contracts() -> None:
    sites = pl.read_parquet(DATA / "sites.parquet")
    assets = pl.read_parquet(DATA / "assets.parquet")
    telemetry = pl.read_parquet(DATA / "telemetry_5min.parquet")
    alarms = pl.read_parquet(DATA / "alarms.parquet")
    orders = pl.read_parquet(DATA / "work_orders.parquet")

    site_ids = set(sites["site_id"])
    asset_ids = set(assets["asset_id"])
    assert set(assets["site_id"]).issubset(site_ids)
    assert set(telemetry["asset_id"]).issubset(asset_ids)
    assert set(alarms["asset_id"]).issubset(asset_ids)
    assert set(orders["asset_id"]).issubset(asset_ids)
    assert assets["asset_id"].n_unique() == assets.height
    assert sites["site_id"].n_unique() == sites.height


def test_failure_patterns_are_observable() -> None:
    telemetry = pl.read_parquet(DATA / "telemetry_5min.parquet")
    assert telemetry.filter(pl.col("vibration_mm_s") >= 7.1).height >= 100
    assert telemetry.filter(pl.col("temperature_c") >= 82).height >= 100
    assert telemetry.filter(pl.col("sensor_status") == "SEM_SINAL").height >= 100
    assert telemetry.select(pl.col("event_ts").n_unique()).item() == 2_016


def test_no_personal_data_columns() -> None:
    forbidden = {
        "name",
        "full_name",
        "email",
        "phone",
        "cpf",
        "document",
        "customer_id",
        "subscriber_id",
    }
    for path in DATA.glob("*.parquet"):
        columns = {column.lower() for column in pl.scan_parquet(path).collect_schema().names()}
        assert columns.isdisjoint(forbidden), (
            f"Coluna pessoal em {path.name}: {columns & forbidden}"
        )
