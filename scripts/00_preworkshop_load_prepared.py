# Databricks notebook source
"""Preparação do instrutor: carrega os Parquet em tabelas managed do Unity Catalog.

Este notebook é executado antes da sessão e não consome tempo da agenda.
"""

# COMMAND ----------

from pathlib import Path

import pandas as pd

dbutils.widgets.text("catalog", "", "Catálogo do workshop")
dbutils.widgets.text("schema", "", "Schema do workshop")

catalog = dbutils.widgets.get("catalog").strip()
schema = dbutils.widgets.get("schema").strip()
if not catalog or not schema:
    raise ValueError("Preencha os widgets 'catalog' e 'schema' antes de executar.")
if any(character in catalog + schema for character in ("`", "\n", "\r", "\x00")):
    raise ValueError("Catálogo ou schema inválido.")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

# COMMAND ----------


def find_data_dir() -> Path:
    """Localiza data/prepared tanto em Databricks Git Folders quanto localmente."""

    candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
    try:
        candidates.extend(Path(__file__).resolve().parents)
    except NameError:
        pass
    for base in candidates:
        candidate = base / "data" / "prepared"
        if (candidate / "manifest.json").exists():
            return candidate
    raise FileNotFoundError(
        "Não encontrei data/prepared. Execute o notebook dentro do Git Folder deste repositório."
    )


data_dir = find_data_dir()
datasets = {
    "prepared_sites": "sites.parquet",
    "prepared_assets": "assets.parquet",
    "prepared_telemetry_5min": "telemetry_5min.parquet",
    "prepared_alarms": "alarms.parquet",
    "prepared_work_orders": "work_orders.parquet",
    "prepared_operating_thresholds": "operating_thresholds.parquet",
}

# COMMAND ----------

results = []
for table_name, file_name in datasets.items():
    pandas_df = pd.read_parquet(data_dir / file_name)
    spark_df = spark.createDataFrame(pandas_df)
    spark_df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table_name)
    results.append((table_name, spark_df.count()))

display(spark.createDataFrame(results, ["table_name", "row_count"]))

# COMMAND ----------

expected = {
    "prepared_sites": 30,
    "prepared_assets": 120,
    "prepared_telemetry_5min": 241_920,
    "prepared_alarms": 480,
    "prepared_work_orders": 240,
    "prepared_operating_thresholds": 18,
}
actual = dict(results)
assert actual == expected, f"Contagens divergentes: {actual}"
print(f"Preparação concluída em {catalog}.{schema}")
