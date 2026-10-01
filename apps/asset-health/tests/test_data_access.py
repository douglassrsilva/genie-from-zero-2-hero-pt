from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from data_access import (
    DataAccessError,
    _quoted_identifier,
    load_local_gold,
    remote_configuration,
)


def _write_gold(data_dir: Path) -> None:
    current = pd.DataFrame(
        {
            "event_ts": ["2026-09-01 12:00:00", "2026-09-01 12:00:00"],
            "asset_id": ["AST-001", "AST-002"],
            "asset_name": ["Bomba 1", "Bomba 2"],
            "site_id": ["SITE-01", "SITE-01"],
            "site_name": ["Estação Norte", "Estação Norte"],
            "operational_region": ["Norte", "Norte"],
            "criticality": ["Alta", "Média"],
            "health_status": ["Crítico", "Saudável"],
            "health_score": [45.0, 92.0],
            "pressure_out_bar": [5.2, 5.8],
            "temperature_c": [83.0, 61.0],
            "flow_m3h": [82.0, 100.0],
            "vibration_mm_s": [7.4, 2.1],
            "power_kw": [74.0, 62.0],
            "active_alarms": [2, 0],
            "recommended_action": ["Inspecionar rolamentos.", "Manter monitoramento."],
        }
    )
    hourly = pd.DataFrame(
        {
            "hour_ts": ["2026-09-01 11:00:00", "2026-09-01 12:00:00"],
            "asset_id": ["AST-001", "AST-001"],
            "site_id": ["SITE-01", "SITE-01"],
            "avg_vibration_mm_s": [6.9, 7.4],
            "avg_temperature_c": [80.0, 83.0],
        }
    )
    current.to_parquet(data_dir / "gold_asset_health_current.parquet", index=False)
    hourly.to_parquet(data_dir / "gold_asset_health_hourly.parquet", index=False)


def test_remote_configuration_requires_all_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("UTILITY_CATALOG", "UTILITY_SCHEMA", "DATABRICKS_WAREHOUSE_ID"):
        monkeypatch.delenv(name, raising=False)

    enabled, missing = remote_configuration()

    assert not enabled
    assert set(missing) == {"UTILITY_CATALOG", "UTILITY_SCHEMA", "DATABRICKS_WAREHOUSE_ID"}


def test_load_local_gold_normalizes_types(tmp_path: Path) -> None:
    _write_gold(tmp_path)

    datasets = load_local_gold(tmp_path)

    assert set(datasets) == {"current", "hourly"}
    assert len(datasets["current"]) == 2
    assert pd.api.types.is_datetime64_any_dtype(datasets["current"]["event_ts"])
    assert pd.api.types.is_datetime64_any_dtype(datasets["hourly"]["hour_ts"])
    assert datasets["current"].loc[0, "health_score"] == 45.0


def test_load_local_gold_reports_missing_files(tmp_path: Path) -> None:
    with pytest.raises(DataAccessError, match="Parquet não encontrado"):
        load_local_gold(tmp_path)


def test_identifier_rejects_control_characters() -> None:
    assert _quoted_identifier("catalogo_demo") == "`catalogo_demo`"
    with pytest.raises(DataAccessError):
        _quoted_identifier("catalogo`invalido")
