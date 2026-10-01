"""Gera os dados sintéticos preparados do workshop de Utilities.

Este utilitário existe apenas para reprodutibilidade. Os participantes recebem os
arquivos Parquet prontos e não executam geração de dados durante o workshop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl

SEED = 42
START_TS = datetime(2026, 9, 21, 0, 0)
POINTS_PER_ASSET = 7 * 24 * 12
ASSET_TYPES = (
    "Bomba centrífuga",
    "Compressor",
    "Motor elétrico",
    "Ventilador industrial",
    "Trocador de calor",
    "Válvula de controle",
)


def _write(df: pl.DataFrame, output_dir: Path, name: str) -> dict[str, object]:
    path = output_dir / f"{name}.parquet"
    df.write_parquet(path, compression="zstd", statistics=True)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"arquivo": path.name, "linhas": df.height, "sha256": digest}


def build_sites() -> pl.DataFrame:
    regions = (
        ("Norte", "AM"),
        ("Nordeste", "BA"),
        ("Centro-Oeste", "GO"),
        ("Sudeste", "RJ"),
        ("Sudeste", "SP"),
        ("Sul", "RS"),
    )
    site_types = ("Estação de bombeamento", "Estação de compressão", "Planta de tratamento")
    rows = []
    for idx in range(30):
        region, state = regions[idx % len(regions)]
        rows.append(
            {
                "site_id": f"SITE-{idx + 1:03d}",
                "site_name": f"Unidade Operacional {idx + 1:02d}",
                "operational_region": region,
                "state_code": state,
                "site_type": site_types[idx % len(site_types)],
                "commissioned_date": date(2012 + (idx % 12), 1 + (idx % 12), 1 + (idx % 25)),
                "nominal_capacity_m3h": float(1_800 + (idx % 10) * 220),
                "latitude_band": f"FAIXA-{1 + idx % 5}",
            }
        )
    return pl.DataFrame(rows)


def build_assets(sites: pl.DataFrame) -> pl.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for site_idx, site in enumerate(sites.iter_rows(named=True)):
        for position in range(4):
            idx = site_idx * 4 + position
            asset_type = ASSET_TYPES[idx % len(ASSET_TYPES)]
            criticality = ("Alta", "Alta", "Média", "Baixa")[position]
            nominal_pressure = (12.0, 18.0, 8.0, 6.0, 10.0, 14.0)[idx % len(ASSET_TYPES)]
            nominal_flow = (420.0, 310.0, 250.0, 540.0, 380.0, 290.0)[idx % len(ASSET_TYPES)]
            nominal_power = (95.0, 150.0, 110.0, 75.0, 60.0, 35.0)[idx % len(ASSET_TYPES)]
            rows.append(
                {
                    "asset_id": f"AST-{idx + 1:04d}",
                    "asset_name": f"Ativo {idx + 1:04d}",
                    "site_id": site["site_id"],
                    "asset_type": asset_type,
                    "criticality": criticality,
                    "model_family": f"Série U{1 + idx % 8}",
                    "commissioned_date": date(2014 + (idx % 10), 1 + (idx % 12), 1 + (idx % 25)),
                    "nominal_pressure_bar": nominal_pressure,
                    "nominal_flow_m3h": nominal_flow,
                    "nominal_power_kw": nominal_power,
                    "baseline_vibration_mm_s": round(float(rng.uniform(1.4, 3.0)), 2),
                    "baseline_temperature_c": round(float(rng.uniform(48.0, 64.0)), 2),
                }
            )
    return pl.DataFrame(rows)


def _scenario_for(asset_index: int) -> str:
    scenario_cycle = {
        0: "cavitacao",
        5: "desgaste_rolamento",
        10: "obstrucao",
        15: "sobrecarga",
    }
    return scenario_cycle.get(asset_index % 20, "operacao_normal")


def build_telemetry(assets: pl.DataFrame) -> pl.DataFrame:
    timestamps = np.array(
        [START_TS + timedelta(minutes=5 * idx) for idx in range(POINTS_PER_ASSET)],
        dtype="datetime64[us]",
    )
    t = np.arange(POINTS_PER_ASSET)
    daily_wave = np.sin(2 * np.pi * t / 288)
    rows: list[pl.DataFrame] = []

    for asset_index, asset in enumerate(assets.iter_rows(named=True)):
        rng = np.random.default_rng(SEED + asset_index + 1)
        pressure_out = asset["nominal_pressure_bar"] * (1 + 0.025 * daily_wave) + rng.normal(
            0, 0.18, POINTS_PER_ASSET
        )
        pressure_in = pressure_out * 0.72 + rng.normal(0, 0.12, POINTS_PER_ASSET)
        temperature = (
            asset["baseline_temperature_c"]
            + 2.5 * daily_wave
            + rng.normal(0, 0.8, POINTS_PER_ASSET)
        )
        vibration = (
            asset["baseline_vibration_mm_s"]
            + 0.15 * daily_wave
            + rng.normal(0, 0.09, POINTS_PER_ASSET)
        )
        flow = asset["nominal_flow_m3h"] * (1 + 0.07 * daily_wave) + rng.normal(
            0, asset["nominal_flow_m3h"] * 0.012, POINTS_PER_ASSET
        )
        power = asset["nominal_power_kw"] * (0.94 + 0.06 * daily_wave) + rng.normal(
            0, 1.1, POINTS_PER_ASSET
        )
        rotation = 1_750 + 35 * daily_wave + rng.normal(0, 7, POINTS_PER_ASSET)
        valve = 72 + 8 * daily_wave + rng.normal(0, 1.5, POINTS_PER_ASSET)

        scenario = _scenario_for(asset_index)
        if scenario == "cavitacao":
            mask = t >= POINTS_PER_ASSET - 216
            ramp = np.linspace(0, 1, mask.sum())
            vibration[mask] += 4.8 * ramp
            pressure_out[mask] -= asset["nominal_pressure_bar"] * 0.23 * ramp
            flow[mask] -= asset["nominal_flow_m3h"] * 0.28 * ramp
        elif scenario == "desgaste_rolamento":
            mask = t >= POINTS_PER_ASSET - 864
            ramp = np.linspace(0, 1, mask.sum())
            vibration[mask] += 5.4 * ramp
            temperature[mask] += 26 * ramp
        elif scenario == "obstrucao":
            mask = t >= POINTS_PER_ASSET - 288
            ramp = np.linspace(0, 1, mask.sum())
            flow[mask] -= asset["nominal_flow_m3h"] * 0.42 * ramp
            pressure_in[mask] += asset["nominal_pressure_bar"] * 0.25 * ramp
            power[mask] += asset["nominal_power_kw"] * 0.18 * ramp
        elif scenario == "sobrecarga":
            mask = t >= POINTS_PER_ASSET - 144
            ramp = np.linspace(0, 1, mask.sum())
            power[mask] += asset["nominal_power_kw"] * 0.45 * ramp
            temperature[mask] += 32 * ramp
            rotation[mask] += 210 * ramp

        offline = rng.random(POINTS_PER_ASSET) < 0.0015
        status = np.where(
            offline,
            "SEM_SINAL",
            np.where(vibration > 7.1, "CRÍTICO", np.where(temperature > 80, "ATENÇÃO", "NORMAL")),
        )
        rows.append(
            pl.DataFrame(
                {
                    "event_ts": timestamps,
                    "asset_id": [asset["asset_id"]] * POINTS_PER_ASSET,
                    "pressure_in_bar": np.round(pressure_in, 3),
                    "pressure_out_bar": np.round(pressure_out, 3),
                    "temperature_c": np.round(temperature, 3),
                    "rotation_rpm": np.round(rotation, 2),
                    "vibration_mm_s": np.round(np.clip(vibration, 0, None), 3),
                    "flow_m3h": np.round(np.clip(flow, 0, None), 3),
                    "power_kw": np.round(np.clip(power, 0, None), 3),
                    "valve_position_pct": np.round(np.clip(valve, 0, 100), 2),
                    "sensor_status": status,
                }
            )
        )
    return pl.concat(rows, rechunk=True)


def build_thresholds() -> pl.DataFrame:
    base_by_type = {
        "Bomba centrífuga": (70.0, 82.0, 4.5, 7.1, 0.78, 0.62),
        "Compressor": (78.0, 92.0, 4.8, 7.1, 0.80, 0.65),
        "Motor elétrico": (75.0, 90.0, 4.5, 7.1, 0.76, 0.60),
        "Ventilador industrial": (72.0, 86.0, 4.8, 7.1, 0.75, 0.58),
        "Trocador de calor": (82.0, 96.0, 4.5, 7.1, 0.78, 0.62),
        "Válvula de controle": (68.0, 80.0, 4.5, 7.1, 0.72, 0.55),
    }
    rows = []
    for asset_type, values in base_by_type.items():
        temp_warning, temp_critical, vib_warning, vib_critical, flow_warning, flow_critical = values
        rows.extend(
            [
                {
                    "asset_type": asset_type,
                    "metric_name": "temperature_c",
                    "warning_min": None,
                    "warning_max": temp_warning,
                    "critical_min": None,
                    "critical_max": temp_critical,
                    "unit": "°C",
                },
                {
                    "asset_type": asset_type,
                    "metric_name": "vibration_mm_s",
                    "warning_min": None,
                    "warning_max": vib_warning,
                    "critical_min": None,
                    "critical_max": vib_critical,
                    "unit": "mm/s",
                },
                {
                    "asset_type": asset_type,
                    "metric_name": "flow_ratio",
                    "warning_min": flow_warning,
                    "warning_max": None,
                    "critical_min": flow_critical,
                    "critical_max": None,
                    "unit": "razão",
                },
            ]
        )
    return pl.DataFrame(
        rows,
        schema_overrides={
            "warning_min": pl.Float64,
            "warning_max": pl.Float64,
            "critical_min": pl.Float64,
            "critical_max": pl.Float64,
        },
    )


def build_alarms(assets: pl.DataFrame) -> pl.DataFrame:
    rng = np.random.default_rng(SEED + 500)
    alarm_types = (
        "Vibração alta",
        "Temperatura alta",
        "Baixa vazão",
        "Pressão instável",
        "Sobrecarga",
        "Falha de comunicação",
    )
    severities = ("Baixa", "Média", "Alta", "Crítica")
    rows = []
    for idx in range(480):
        asset_index = int(rng.integers(0, assets.height))
        asset = assets.row(asset_index, named=True)
        opened = START_TS + timedelta(minutes=int(rng.integers(0, 7 * 24 * 60)))
        active = idx % 7 == 0 or (asset_index % 20 in {0, 5, 10, 15} and idx % 5 == 0)
        duration_minutes = int(rng.integers(20, 720))
        closed = None if active else opened + timedelta(minutes=duration_minutes)
        alarm_type = alarm_types[(asset_index + idx) % len(alarm_types)]
        severity = severities[
            (idx + (2 if asset_index % 20 in {0, 5, 10, 15} else 0)) % len(severities)
        ]
        rows.append(
            {
                "alarm_id": f"ALM-{idx + 1:05d}",
                "asset_id": asset["asset_id"],
                "site_id": asset["site_id"],
                "opened_ts": opened,
                "closed_ts": closed,
                "severity": severity,
                "alarm_type": alarm_type,
                "status": "Aberto" if active else "Fechado",
                "description": f"Evento sintético: {alarm_type.lower()}",
            }
        )
    return pl.DataFrame(rows, schema_overrides={"closed_ts": pl.Datetime("us")})


def build_work_orders(assets: pl.DataFrame) -> pl.DataFrame:
    rng = np.random.default_rng(SEED + 900)
    work_types = ("Inspeção", "Manutenção preventiva", "Manutenção corretiva", "Calibração")
    priorities = ("Baixa", "Média", "Alta", "Urgente")
    causes = ("Desgaste", "Cavitação", "Obstrução", "Sobrecarga", "Instrumentação", "Rotina")
    rows = []
    for idx in range(240):
        asset_index = int(rng.integers(0, assets.height))
        asset = assets.row(asset_index, named=True)
        created = (
            START_TS
            - timedelta(days=int(rng.integers(0, 21)))
            + timedelta(minutes=int(rng.integers(0, 7 * 24 * 60)))
        )
        completed = idx % 6 != 0
        completion_ts = (
            created + timedelta(hours=float(rng.uniform(1.5, 36))) if completed else None
        )
        rows.append(
            {
                "work_order_id": f"OS-{idx + 1:05d}",
                "asset_id": asset["asset_id"],
                "site_id": asset["site_id"],
                "created_ts": created,
                "completed_ts": completion_ts,
                "work_type": work_types[idx % len(work_types)],
                "priority": priorities[(idx + asset_index) % len(priorities)],
                "status": "Concluída" if completed else "Aberta",
                "downtime_hours": round(float(rng.uniform(0.2, 16.0)) if completed else 0.0, 2),
                "estimated_cost_brl": round(float(rng.uniform(450, 18_000)), 2),
                "cause_code": causes[(idx + asset_index) % len(causes)],
            }
        )
    return pl.DataFrame(rows, schema_overrides={"completed_ts": pl.Datetime("us")})


def validate(
    sites: pl.DataFrame,
    assets: pl.DataFrame,
    telemetry: pl.DataFrame,
    alarms: pl.DataFrame,
    work_orders: pl.DataFrame,
    thresholds: pl.DataFrame,
) -> None:
    expected = {
        "sites": 30,
        "assets": 120,
        "telemetry": 241_920,
        "alarms": 480,
        "work_orders": 240,
        "thresholds": 18,
    }
    actual = {
        "sites": sites.height,
        "assets": assets.height,
        "telemetry": telemetry.height,
        "alarms": alarms.height,
        "work_orders": work_orders.height,
        "thresholds": thresholds.height,
    }
    if actual != expected:
        raise ValueError(f"Contagens inesperadas: {actual}")
    asset_ids = set(assets["asset_id"].to_list())
    site_ids = set(sites["site_id"].to_list())
    if not set(telemetry["asset_id"].unique()).issubset(asset_ids):
        raise ValueError("Telemetria contém asset_id órfão")
    if not set(assets["site_id"].unique()).issubset(site_ids):
        raise ValueError("Ativos contêm site_id órfão")
    critical_points = telemetry.filter(
        (pl.col("vibration_mm_s") > 7.1) | (pl.col("temperature_c") > 82)
    ).height
    if critical_points < 100:
        raise ValueError("Os cenários determinísticos não produziram pontos críticos suficientes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/prepared"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    sites = build_sites()
    assets = build_assets(sites)
    telemetry = build_telemetry(assets)
    alarms = build_alarms(assets)
    work_orders = build_work_orders(assets)
    thresholds = build_thresholds()
    validate(sites, assets, telemetry, alarms, work_orders, thresholds)

    manifest = {
        "seed": SEED,
        "inicio_telemetria": START_TS.isoformat(),
        "fim_telemetria": (START_TS + timedelta(minutes=5 * (POINTS_PER_ASSET - 1))).isoformat(),
        "dados_pessoais": False,
        "arquivos": [
            _write(sites, args.output, "sites"),
            _write(assets, args.output, "assets"),
            _write(telemetry, args.output, "telemetry_5min"),
            _write(alarms, args.output, "alarms"),
            _write(work_orders, args.output, "work_orders"),
            _write(thresholds, args.output, "operating_thresholds"),
        ],
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
