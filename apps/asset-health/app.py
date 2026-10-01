"""App básica de saúde de ativos para o workshop Genie do Zero ao Herói."""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from data_access import load_local_gold, load_remote_gold, remote_configuration

st.set_page_config(
    page_title="Saúde de ativos",
    page_icon="⚙️",
    layout="wide",
)


@st.cache_data(ttl=120, show_spinner="Consultando as tabelas Gold...")
def _load_remote(catalog: str, schema: str, warehouse_id: str) -> dict[str, pd.DataFrame]:
    return load_remote_gold(catalog, schema, warehouse_id)


@st.cache_data(show_spinner=False)
def _load_local() -> dict[str, pd.DataFrame]:
    return load_local_gold()


def _options(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame:
        return []
    return sorted(frame[column].dropna().astype(str).unique().tolist())


def _filter(frame: pd.DataFrame, column: str, selected: str, all_label: str) -> pd.DataFrame:
    if selected == all_label or column not in frame:
        return frame
    return frame[frame[column].astype(str) == selected]


def _integer(value: float) -> str:
    return f"{int(value):,}".replace(",", ".")


def _critical_mask(frame: pd.DataFrame) -> pd.Series:
    if "health_status" not in frame:
        return pd.Series(False, index=frame.index)
    return frame["health_status"].astype(str).str.casefold().str.contains("crít|crit", regex=True)


def _load_datasets() -> tuple[dict[str, pd.DataFrame], str, str, list[str]]:
    remote_enabled, missing = remote_configuration()
    if remote_enabled:
        try:
            datasets = _load_remote(
                os.environ["UTILITY_CATALOG"],
                os.environ["UTILITY_SCHEMA"],
                os.environ["DATABRICKS_WAREHOUSE_ID"],
            )
            return datasets, "Unity Catalog · tabelas Gold", "", missing
        except Exception as exc:  # noqa: BLE001 - a contingência é intencional no workshop.
            try:
                datasets = _load_local()
            except Exception as local_exc:
                raise RuntimeError(
                    "A consulta remota falhou e a contingência local não está disponível. "
                    f"Remoto: {exc}. Local: {local_exc}"
                ) from local_exc
            return datasets, "Parquet local · contingência", str(exc), missing

    return _load_local(), "Parquet local · contingência", "", missing


def main() -> None:
    st.title("⚙️ Saúde operacional de ativos")
    st.caption("Estações, bombas e telemetria sintética · da camada Gold à decisão operacional")

    try:
        datasets, source, remote_error, missing = _load_datasets()
    except Exception as exc:  # noqa: BLE001
        st.error("Não foi possível carregar os dados da aplicação.")
        st.code(str(exc))
        st.stop()

    current = datasets["current"].copy()
    hourly = datasets["hourly"].copy()

    if remote_error:
        st.warning(
            "A consulta ao Unity Catalog não respondeu; a demonstração continuou com "
            "os dados Parquet locais."
        )
    elif missing and any(
        os.getenv(name) for name in ("UTILITY_CATALOG", "UTILITY_SCHEMA", "DATABRICKS_WAREHOUSE_ID")
    ):
        st.info(f"Configuração remota incompleta. Faltam: {', '.join(missing)}.")

    st.caption(f"Fonte em uso: {source}")

    st.sidebar.header("Filtros operacionais")
    region = st.sidebar.selectbox(
        "Região",
        ["Todas", *_options(current, "operational_region")],
    )
    filtered = _filter(current, "operational_region", region, "Todas")

    site = st.sidebar.selectbox(
        "Estação",
        ["Todas", *_options(filtered, "site_name")],
    )
    filtered = _filter(filtered, "site_name", site, "Todas")

    criticality = st.sidebar.selectbox(
        "Criticidade",
        ["Todas", *_options(filtered, "criticality")],
    )
    filtered = _filter(filtered, "criticality", criticality, "Todas")

    asset_labels = filtered.assign(
        _asset_label=filtered["asset_name"].astype(str) + " · " + filtered["asset_id"].astype(str)
    )
    asset = st.sidebar.selectbox(
        "Ativo",
        ["Todos", *_options(asset_labels, "_asset_label")],
    )
    if asset != "Todos":
        selected_asset_id = asset.rsplit(" · ", 1)[-1]
        filtered = filtered[filtered["asset_id"].astype(str) == selected_asset_id]
    else:
        selected_asset_id = None

    critical_assets = int(_critical_mask(filtered).sum())
    health_score = pd.to_numeric(filtered["health_score"], errors="coerce").mean()
    active_alarms = pd.to_numeric(filtered["active_alarms"], errors="coerce").sum()

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Ativos monitorados", _integer(filtered["asset_id"].nunique()))
    metric_2.metric("Ativos críticos", _integer(critical_assets))
    metric_3.metric(
        "Índice médio de saúde", f"{health_score:.1f}/100" if pd.notna(health_score) else "—"
    )
    metric_4.metric("Alarmes ativos", _integer(active_alarms))

    st.subheader("Ativos priorizados")
    priority_columns = [
        "asset_id",
        "asset_name",
        "site_name",
        "operational_region",
        "criticality",
        "health_status",
        "health_score",
        "vibration_mm_s",
        "temperature_c",
        "active_alarms",
        "recommended_action",
    ]
    priority = filtered.sort_values(
        ["health_score", "active_alarms"],
        ascending=[True, False],
    )
    st.dataframe(
        priority[priority_columns].head(25),
        hide_index=True,
        width="stretch",
        column_config={
            "asset_id": "ID",
            "asset_name": "Ativo",
            "site_name": "Estação",
            "operational_region": "Região",
            "criticality": "Criticidade",
            "health_status": "Condição",
            "health_score": st.column_config.ProgressColumn(
                "Saúde",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "vibration_mm_s": st.column_config.NumberColumn("Vibração (mm/s)", format="%.2f"),
            "temperature_c": st.column_config.NumberColumn("Temperatura (°C)", format="%.1f"),
            "active_alarms": "Alarmes",
            "recommended_action": "Ação recomendada",
        },
    )

    st.subheader("Tendência de vibração e temperatura")
    trend_assets = priority["asset_id"].dropna().astype(str).unique().tolist()
    if selected_asset_id:
        trend_asset_id = selected_asset_id
    elif trend_assets:
        trend_asset_id = st.selectbox(
            "Ativo para análise temporal",
            trend_assets,
            format_func=lambda value: (
                filtered.loc[filtered["asset_id"].astype(str) == value, "asset_name"].iloc[0]
                if not filtered.loc[filtered["asset_id"].astype(str) == value].empty
                else value
            ),
        )
    else:
        trend_asset_id = None

    trend = (
        hourly[hourly["asset_id"].astype(str) == str(trend_asset_id)].copy()
        if trend_asset_id
        else pd.DataFrame()
    )
    if trend.empty:
        st.info("Não há série temporal disponível para os filtros selecionados.")
    else:
        long_trend = trend.melt(
            id_vars=["hour_ts"],
            value_vars=["avg_vibration_mm_s", "avg_temperature_c"],
            var_name="metric",
            value_name="value",
        )
        long_trend["metric"] = long_trend["metric"].map(
            {
                "avg_vibration_mm_s": "Vibração média (mm/s)",
                "avg_temperature_c": "Temperatura média (°C)",
            }
        )
        figure = px.line(
            long_trend,
            x="hour_ts",
            y="value",
            color="metric",
            facet_row="metric",
            labels={"hour_ts": "Hora", "value": "Valor", "metric": "Métrica"},
            markers=False,
        )
        figure.update_yaxes(matches=None)
        figure.for_each_annotation(
            lambda annotation: annotation.update(text=annotation.text.split("=")[-1])
        )
        figure.update_layout(height=470, legend_title_text="Métrica")
        st.plotly_chart(figure, width="stretch")

    st.subheader("Recomendação operacional")
    recommendation_row = priority.head(1)
    if recommendation_row.empty:
        st.info("Selecione filtros com dados para obter uma recomendação.")
    else:
        row = recommendation_row.iloc[0]
        st.info(f"**{row['asset_name']} ({row['asset_id']})** — {row['recommended_action']}")
        st.caption(
            "Recomendação baseada em regras didáticas. Uma decisão operacional real "
            "deve seguir os procedimentos de segurança e manutenção da organização."
        )

    st.divider()
    st.caption(
        "Desafio: modernize a navegação, acrescente contexto do ativo e transforme a "
        "recomendação em um fluxo de ação."
    )


if __name__ == "__main__":
    main()
