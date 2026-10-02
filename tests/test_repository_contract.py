from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_expected_workshop_assets_exist() -> None:
    expected = [
        "labs/00_load_prepared.py",
        "labs/01_create_gold.sql",
        "labs/02_create_metric_views.sql",
        "labs/03_validation_queries.sql",
        "config/genie_agent_instructions.md",
        "config/domain_page_content.md",
        "apps/asset-health/app.py",
        "docs/INSTRUCTOR_RUNBOOK.md",
    ]
    for relative in expected:
        assert (ROOT / relative).exists(), relative


def test_sql_is_parameterized() -> None:
    for path in (ROOT / "labs").glob("*.sql"):
        content = path.read_text(encoding="utf-8")
        assert "workshop_catalog" in content
        assert "workshop_schema" in content
        assert "cloud.databricks.com" not in content
        assert not re.search(r"(?i)(token|password|client_secret)\s*=\s*['\"][^'\"]+", content)


def test_gold_contract_for_app() -> None:
    sql = (ROOT / "labs" / "01_create_gold.sql").read_text(encoding="utf-8")
    current_columns = {
        "asset_id",
        "asset_name",
        "site_id",
        "site_name",
        "operational_region",
        "criticality",
        "health_status",
        "health_score",
        "pressure_out_bar",
        "temperature_c",
        "flow_m3h",
        "vibration_mm_s",
        "power_kw",
        "active_alarms",
        "recommended_action",
        "event_ts",
    }
    hourly_columns = {
        "hour_ts",
        "asset_id",
        "site_id",
        "avg_vibration_mm_s",
        "avg_temperature_c",
    }
    assert all(column in sql for column in current_columns | hourly_columns)


def test_visible_loader_matches_instructor_compatibility_copy() -> None:
    lab_loader = (ROOT / "labs" / "00_load_prepared.py").read_text(encoding="utf-8")
    script_loader = (ROOT / "scripts" / "00_preworkshop_load_prepared.py").read_text(
        encoding="utf-8"
    )
    assert lab_loader == script_loader
    for table_name in (
        "prepared_sites",
        "prepared_assets",
        "prepared_telemetry_5min",
        "prepared_alarms",
        "prepared_work_orders",
        "prepared_operating_thresholds",
    ):
        assert table_name in lab_loader


def test_no_generated_caches_are_versionable() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "__pycache__/" in gitignore
    assert ".env" in gitignore
    assert ".databricks/" in gitignore
