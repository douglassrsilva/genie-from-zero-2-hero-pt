"""Acesso às tabelas Gold da App de saúde de ativos.

Em Databricks Apps, as consultas usam a identidade de serviço injetada pela
plataforma. Fora do workspace, a contingência lê Parquet sintético em
``data/prepared`` e não exige credenciais.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

CURRENT_TABLE: Final = "gold_asset_health_current"
HOURLY_TABLE: Final = "gold_asset_health_hourly"
REMOTE_VARIABLES: Final = (
    "UTILITY_CATALOG",
    "UTILITY_SCHEMA",
    "DATABRICKS_WAREHOUSE_ID",
)

APP_DIR: Final = Path(__file__).resolve().parent
DEFAULT_DATA_DIR: Final = APP_DIR.parents[1] / "data" / "prepared"


class DataAccessError(RuntimeError):
    """Erro legível de configuração ou acesso aos dados."""


def remote_configuration() -> tuple[bool, list[str]]:
    """Retorna se as três variáveis necessárias ao modo remoto estão definidas."""

    missing = [name for name in REMOTE_VARIABLES if not os.getenv(name, "").strip()]
    return not missing, missing


def _quoted_identifier(value: str) -> str:
    """Protege identificadores recebidos por variável de ambiente."""

    value = value.strip()
    if not value or any(character in value for character in ("`", "\n", "\r", "\x00")):
        raise DataAccessError("Identificador inválido na configuração do Unity Catalog.")
    return f"`{value}`"


def _workspace_client():
    """Cria um cliente com a identidade padrão do App ou do ambiente local."""

    from databricks.sdk import WorkspaceClient

    return WorkspaceClient()


def _state_name(response) -> str:
    state = response.status.state if response.status else None
    return getattr(state, "value", str(state or "UNKNOWN"))


def _statement_to_dataframe(statement: str, warehouse_id: str, row_limit: int) -> pd.DataFrame:
    """Executa SQL pelo Statement Execution API e reúne todos os chunks."""

    client = _workspace_client()
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=statement,
        wait_timeout="50s",
        row_limit=row_limit,
    )
    state = _state_name(response)
    if state != "SUCCEEDED":
        error = response.status.error if response.status else None
        message = getattr(error, "message", None) or state
        raise DataAccessError(f"A consulta SQL não foi concluída: {message}")

    manifest = response.manifest
    if not manifest or not manifest.schema:
        return pd.DataFrame()

    columns = [column.name for column in (manifest.schema.columns or [])]
    rows = list(response.result.data_array or []) if response.result else []
    chunks = manifest.chunks or []
    for chunk in chunks[1:]:
        result = client.statement_execution.get_statement_result_chunk_n(
            statement_id=response.statement_id,
            chunk_index=chunk.chunk_index,
        )
        rows.extend(result.data_array or [])
    return pd.DataFrame(rows, columns=columns)


def load_remote_gold(catalog: str, schema: str, warehouse_id: str) -> dict[str, pd.DataFrame]:
    """Carrega as duas Gold parametrizadas pelo ambiente do Databricks App."""

    catalog_id = _quoted_identifier(catalog)
    schema_id = _quoted_identifier(schema)
    namespace = f"{catalog_id}.{schema_id}"

    try:
        configured_limit = int(os.getenv("UTILITY_APP_HOURLY_ROW_LIMIT", "100000"))
    except ValueError as exc:
        raise DataAccessError("UTILITY_APP_HOURLY_ROW_LIMIT deve ser um número inteiro.") from exc
    hourly_limit = min(max(configured_limit, 1_000), 500_000)

    current = _statement_to_dataframe(
        f"SELECT * FROM {namespace}.{_quoted_identifier(CURRENT_TABLE)} LIMIT 10000",
        warehouse_id,
        10_000,
    )
    hourly = _statement_to_dataframe(
        f"SELECT * FROM {namespace}.{_quoted_identifier(HOURLY_TABLE)} LIMIT {hourly_limit}",
        warehouse_id,
        hourly_limit,
    )
    return normalize_gold_contract({"current": current, "hourly": hourly})


def _find_parquet(data_dir: Path, names: tuple[str, ...], required: bool = True) -> Path | None:
    for name in names:
        candidate = data_dir / f"{name}.parquet"
        if candidate.exists():
            return candidate
    if required:
        expected = ", ".join(f"{name}.parquet" for name in names)
        raise DataAccessError(f"Arquivo Parquet não encontrado em {data_dir}: {expected}.")
    return None


def _read_parquet(data_dir: Path, names: tuple[str, ...], required: bool = True) -> pd.DataFrame:
    path = _find_parquet(data_dir, names, required=required)
    return pd.read_parquet(path) if path else pd.DataFrame()


def _derive_local_gold(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Deriva uma contingência pequena quando somente as fontes preparadas existem."""

    assets = _read_parquet(data_dir, ("dim_assets", "assets"))
    sites = _read_parquet(data_dir, ("dim_sites", "sites"))
    telemetry = _read_parquet(
        data_dir,
        ("fact_telemetry_5min", "telemetry_5min", "telemetry"),
    )
    alarms = _read_parquet(data_dir, ("fact_alarms", "alarms"), required=False)

    required = {"event_ts", "asset_id"}
    if not required.issubset(telemetry.columns):
        raise DataAccessError("A telemetria local precisa conter event_ts e asset_id.")

    telemetry = telemetry.copy()
    telemetry["event_ts"] = pd.to_datetime(telemetry["event_ts"], errors="coerce")
    telemetry = telemetry.dropna(subset=["event_ts", "asset_id"])
    if telemetry.empty:
        raise DataAccessError("A telemetria local não contém registros válidos.")

    current = telemetry.sort_values("event_ts").groupby("asset_id", as_index=False).tail(1)
    if "asset_id" in assets:
        asset_columns = [
            column
            for column in ("asset_id", "asset_name", "site_id", "criticality")
            if column in assets
        ]
        current = current.merge(
            assets[asset_columns].drop_duplicates("asset_id"),
            on="asset_id",
            how="left",
            suffixes=("", "_asset"),
        )
        if "site_id_asset" in current:
            current["site_id"] = current.get("site_id").fillna(current["site_id_asset"])
            current = current.drop(columns="site_id_asset")

    if "site_id" in current and "site_id" in sites:
        site_columns = [
            column for column in ("site_id", "site_name", "operational_region") if column in sites
        ]
        current = current.merge(
            sites[site_columns].drop_duplicates("site_id"),
            on="site_id",
            how="left",
            suffixes=("", "_site"),
        )

    current["active_alarms"] = 0
    if not alarms.empty and "asset_id" in alarms:
        active = alarms.copy()
        if "status" in active:
            active = active[
                ~active["status"].astype(str).str.casefold().isin({"closed", "fechado", "fechada"})
            ]
        alarm_count = active.groupby("asset_id").size()
        current["active_alarms"] = current["asset_id"].map(alarm_count).fillna(0)

    vibration = pd.to_numeric(current.get("vibration_mm_s", 0), errors="coerce").fillna(0)
    temperature = pd.to_numeric(current.get("temperature_c", 0), errors="coerce").fillna(0)
    score = (
        100
        - (vibration - 3.5).clip(lower=0) * 7
        - (temperature - 65).clip(lower=0) * 1.3
        - current["active_alarms"] * 8
    ).clip(0, 100)
    current["health_score"] = score.round(1)
    current["health_status"] = np.select(
        [score < 60, score < 80],
        ["Crítico", "Atenção"],
        default="Saudável",
    )
    current["recommended_action"] = np.select(
        [score < 60, vibration >= 4.5, temperature >= 75],
        [
            "Inspecionar o ativo imediatamente e validar os alarmes associados.",
            "Verificar alinhamento, rolamentos e tendência de vibração.",
            "Revisar refrigeração, carga e condição térmica do ativo.",
        ],
        default="Manter monitoramento e rotina preventiva.",
    )

    for column in ("vibration_mm_s", "temperature_c"):
        if column not in telemetry:
            telemetry[column] = np.nan
    telemetry["hour_ts"] = telemetry["event_ts"].dt.floor("h")
    hourly = (
        telemetry.groupby(["hour_ts", "asset_id"], as_index=False)
        .agg(
            avg_vibration_mm_s=("vibration_mm_s", "mean"),
            avg_temperature_c=("temperature_c", "mean"),
        )
        .sort_values(["asset_id", "hour_ts"])
    )
    if "site_id" in current:
        hourly = hourly.merge(
            current[["asset_id", "site_id"]].drop_duplicates("asset_id"),
            on="asset_id",
            how="left",
        )
    return {"current": current, "hourly": hourly}


def load_local_gold(data_dir: Path | str | None = None) -> dict[str, pd.DataFrame]:
    """Lê Gold em Parquet ou as deriva das fontes preparadas do workshop."""

    configured_dir = os.getenv("UTILITY_DATA_DIR", "").strip()
    root = Path(data_dir or configured_dir or DEFAULT_DATA_DIR).expanduser().resolve()

    current_path = _find_parquet(
        root,
        (CURRENT_TABLE, "asset_health_current"),
        required=False,
    )
    hourly_path = _find_parquet(
        root,
        (HOURLY_TABLE, "asset_health_hourly"),
        required=False,
    )
    if current_path and hourly_path:
        return normalize_gold_contract(
            {
                "current": pd.read_parquet(current_path),
                "hourly": pd.read_parquet(hourly_path),
            }
        )
    return normalize_gold_contract(_derive_local_gold(root))


def _rename_aliases(frame: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    rename = {
        source: target
        for source, target in aliases.items()
        if source in frame and target not in frame
    }
    return frame.rename(columns=rename).copy()


def _ensure_columns(frame: pd.DataFrame, defaults: dict[str, object]) -> pd.DataFrame:
    frame = frame.copy()
    for column, default in defaults.items():
        if column not in frame:
            frame[column] = default
    return frame


def normalize_gold_contract(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Normaliza tipos e mantém a interface estável entre SQL e Parquet."""

    current = _rename_aliases(
        datasets.get("current", pd.DataFrame()),
        {
            "region": "operational_region",
            "station_name": "site_name",
            "status_saude": "health_status",
            "indice_saude": "health_score",
            "open_alarms": "active_alarms",
        },
    )
    current = _ensure_columns(
        current,
        {
            "event_ts": pd.NaT,
            "asset_id": "",
            "asset_name": "Ativo não informado",
            "site_id": "",
            "site_name": "Estação não informada",
            "operational_region": "Região não informada",
            "criticality": "Não informada",
            "health_status": "Não informado",
            "health_score": 0.0,
            "pressure_out_bar": np.nan,
            "temperature_c": np.nan,
            "flow_m3h": np.nan,
            "vibration_mm_s": np.nan,
            "power_kw": np.nan,
            "active_alarms": 0,
            "recommended_action": "Validar a condição do ativo com a equipe operacional.",
        },
    )
    current["event_ts"] = pd.to_datetime(current["event_ts"], errors="coerce")
    for column in (
        "health_score",
        "pressure_out_bar",
        "temperature_c",
        "flow_m3h",
        "vibration_mm_s",
        "power_kw",
        "active_alarms",
    ):
        current[column] = pd.to_numeric(current[column], errors="coerce")
    current["health_score"] = current["health_score"].fillna(0).clip(0, 100)
    current["active_alarms"] = current["active_alarms"].fillna(0).clip(lower=0)

    hourly = _rename_aliases(
        datasets.get("hourly", pd.DataFrame()),
        {
            "metric_hour": "hour_ts",
            "event_hour": "hour_ts",
            "avg_vibration": "avg_vibration_mm_s",
            "avg_temperature": "avg_temperature_c",
        },
    )
    hourly = _ensure_columns(
        hourly,
        {
            "hour_ts": pd.NaT,
            "asset_id": "",
            "site_id": "",
            "avg_vibration_mm_s": np.nan,
            "avg_temperature_c": np.nan,
        },
    )
    hourly["hour_ts"] = pd.to_datetime(hourly["hour_ts"], errors="coerce")
    for column in ("avg_vibration_mm_s", "avg_temperature_c"):
        hourly[column] = pd.to_numeric(hourly[column], errors="coerce")
    hourly = hourly.dropna(subset=["hour_ts"]).sort_values(["asset_id", "hour_ts"])

    return {"current": current, "hourly": hourly}
