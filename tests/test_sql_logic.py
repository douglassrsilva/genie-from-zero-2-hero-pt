from __future__ import annotations

import re
from pathlib import Path

import duckdb
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "prepared"


def _gold_queries() -> list[tuple[str, str]]:
    sql = (ROOT / "labs" / "01_create_gold.sql").read_text(encoding="utf-8")
    pattern = re.compile(
        r"CREATE OR REPLACE TABLE\s+(\w+)\s+COMMENT\s+'[^']*'\s+"
        r"TBLPROPERTIES\s*\([^)]*\)\s+AS\s+(.*?);",
        flags=re.DOTALL | re.IGNORECASE,
    )
    return pattern.findall(sql)


def test_gold_sql_logic_against_prepared_parquet() -> None:
    connection = duckdb.connect(":memory:")
    sources = {
        "prepared_sites": "sites.parquet",
        "prepared_assets": "assets.parquet",
        "prepared_telemetry_5min": "telemetry_5min.parquet",
        "prepared_alarms": "alarms.parquet",
        "prepared_work_orders": "work_orders.parquet",
        "prepared_operating_thresholds": "operating_thresholds.parquet",
    }
    for table, filename in sources.items():
        path = (DATA / filename).as_posix().replace("'", "''")
        connection.execute(f"CREATE VIEW {table} AS SELECT * FROM read_parquet('{path}')")

    queries = _gold_queries()
    assert [name for name, _ in queries] == [
        "gold_asset_health_current",
        "gold_asset_health_hourly",
        "gold_site_operations_daily",
        "gold_maintenance_impact",
    ]
    for name, query in queries:
        # Única adaptação de dialeto: Databricks usa * EXCEPT, DuckDB usa * EXCLUDE.
        local_query = query.replace("* EXCEPT (rn)", "* EXCLUDE (rn)")
        connection.execute(f"CREATE OR REPLACE TABLE {name} AS {local_query}")

    counts = {
        name: connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name, _ in queries
    }
    assert counts == {
        "gold_asset_health_current": 120,
        "gold_asset_health_hourly": 20_160,
        "gold_site_operations_daily": 210,
        "gold_maintenance_impact": 240,
    }
    current_summary = connection.execute(
        """
        SELECT
          COUNT(*) FILTER (WHERE health_status = 'Crítico'),
          MIN(health_score),
          MAX(health_score),
          COUNT(*) FILTER (WHERE recommended_action IS NULL)
        FROM gold_asset_health_current
        """
    ).fetchone()
    assert current_summary[0] >= 1
    assert 0 <= current_summary[1] <= current_summary[2] <= 100
    assert current_summary[3] == 0


def test_metric_view_yaml_blocks_are_valid() -> None:
    sql = (ROOT / "labs" / "02_create_metric_views.sql").read_text(encoding="utf-8")
    definitions = re.findall(r"AS\s+\$\$(.*?)\$\$;", sql, flags=re.DOTALL | re.IGNORECASE)
    assert len(definitions) == 2
    for raw in definitions:
        definition = yaml.safe_load(raw)
        assert definition["version"] == 1.1
        assert definition["source"].startswith("gold_")
        assert definition["dimensions"]
        assert definition["measures"]
        assert all("display_name" in item for item in definition["dimensions"])
        assert all("synonyms" in item for item in definition["measures"])
