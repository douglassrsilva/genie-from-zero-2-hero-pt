# Databricks notebook source
"""Carrega os Parquet prontos em tabelas managed do Unity Catalog.

Execute uma vez antes do laboratório Gold. Este notebook não gera dados: ele
somente lê os seis arquivos versionados em ``data/prepared`` e cria as tabelas
``prepared_*`` no catálogo e schema informados.
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

namespace = f"`{catalog}`.`{schema}`"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {namespace}")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

# COMMAND ----------


def find_data_dir() -> Path:
    """Localiza data/prepared em um Databricks Git Folder ou checkout local."""

    starting_points = [Path.cwd()]
    try:
        starting_points.append(Path(__file__).resolve().parent)
    except NameError:
        pass
    try:
        notebook_path = (
            dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
        )
        starting_points.append(Path("/Workspace") / notebook_path.lstrip("/"))
    except Exception:
        pass

    checked = []
    for start in starting_points:
        directory = start if start.is_dir() else start.parent
        for base in (directory, *directory.parents):
            candidate = base / "data" / "prepared"
            if candidate in checked:
                continue
            checked.append(candidate)
            if (candidate / "manifest.json").is_file():
                return candidate
    locations = "\n- ".join(str(path) for path in checked[:12])
    raise FileNotFoundError(
        "Não encontrei data/prepared. Abra este notebook dentro do Git Folder "
        f"do workshop. Locais verificados:\n- {locations}"
    )


data_dir = find_data_dir()
datasets = {
    "prepared_sites": ("sites.parquet", 30),
    "prepared_assets": ("assets.parquet", 120),
    "prepared_telemetry_5min": ("telemetry_5min.parquet", 241_920),
    "prepared_alarms": ("alarms.parquet", 480),
    "prepared_work_orders": ("work_orders.parquet", 240),
    "prepared_operating_thresholds": ("operating_thresholds.parquet", 18),
}

missing_files = [
    file_name for file_name, _ in datasets.values() if not (data_dir / file_name).is_file()
]
if missing_files:
    raise FileNotFoundError(f"Arquivos preparados ausentes em {data_dir}: {missing_files}")

print(f"Origem dos Parquet: {data_dir}")
print(f"Destino Unity Catalog: {catalog}.{schema}")

# COMMAND ----------

# Spark não lê Workspace Files de forma distribuída em todas as modalidades de
# compute. Como o pacote tem apenas 241.920 leituras, a carga usa pandas no
# driver e grava tabelas Delta managed com Spark.
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")

results = []
for table_name, (file_name, expected_count) in datasets.items():
    pandas_df = pd.read_parquet(data_dir / file_name)
    if len(pandas_df) != expected_count:
        raise ValueError(
            f"{file_name}: esperado {expected_count:,}, encontrado {len(pandas_df):,}."
        )

    full_table_name = f"{namespace}.`{table_name}`"
    spark_df = spark.createDataFrame(pandas_df)
    (
        spark_df.write.mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(full_table_name)
    )
    spark.sql(
        f"ALTER TABLE {full_table_name} SET TBLPROPERTIES "
        "('workshop.layer' = 'prepared', 'workshop.contains_pii' = 'false')"
    )
    actual_count = spark.sql(f"SELECT COUNT(*) AS row_count FROM {full_table_name}").first()[0]
    if actual_count != expected_count:
        raise AssertionError(
            f"{full_table_name}: esperado {expected_count:,}, gravado {actual_count:,}."
        )
    results.append((table_name, file_name, actual_count, "OK"))

display(
    spark.createDataFrame(
        results,
        ["table_name", "source_file", "row_count", "status"],
    )
)

# COMMAND ----------

missing_tables = [
    table_name
    for table_name in datasets
    if not spark.catalog.tableExists(f"{catalog}.{schema}.{table_name}")
]
assert not missing_tables, f"Tabelas não encontradas após a carga: {missing_tables}"

print("Carga concluída. Agora execute labs/01_create_gold.sql com o mesmo catálogo e schema.")
