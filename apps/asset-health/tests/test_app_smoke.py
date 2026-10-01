from __future__ import annotations

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

APP_DIR = Path(__file__).resolve().parents[1]


def test_streamlit_app_renders_four_kpis(tmp_path: Path, monkeypatch) -> None:
    current = pd.DataFrame(
        {
            "event_ts": ["2026-09-01 12:00:00"],
            "asset_id": ["AST-001"],
            "asset_name": ["Bomba 1"],
            "site_id": ["SITE-01"],
            "site_name": ["Estação Norte"],
            "operational_region": ["Norte"],
            "criticality": ["Alta"],
            "health_status": ["Crítico"],
            "health_score": [45.0],
            "pressure_out_bar": [5.2],
            "temperature_c": [83.0],
            "flow_m3h": [82.0],
            "vibration_mm_s": [7.4],
            "power_kw": [74.0],
            "active_alarms": [2],
            "recommended_action": ["Inspecionar rolamentos."],
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
    current.to_parquet(tmp_path / "gold_asset_health_current.parquet", index=False)
    hourly.to_parquet(tmp_path / "gold_asset_health_hourly.parquet", index=False)

    monkeypatch.setenv("UTILITY_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("UTILITY_CATALOG", raising=False)
    monkeypatch.delenv("UTILITY_SCHEMA", raising=False)
    monkeypatch.delenv("DATABRICKS_WAREHOUSE_ID", raising=False)

    app = AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=30).run()

    assert not app.exception
    assert len(app.metric) == 4
    assert app.metric[0].label == "Ativos monitorados"
    assert app.metric[1].value == "1"
