-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Laboratório 1 — camada Gold
-- MAGIC
-- MAGIC Edite somente os dois valores abaixo. As seis tabelas `prepared_*` já
-- MAGIC devem ter sido carregadas pelo instrutor.

-- COMMAND ----------

DECLARE OR REPLACE VARIABLE workshop_catalog STRING DEFAULT 'PREENCHA_O_CATALOGO';
DECLARE OR REPLACE VARIABLE workshop_schema STRING DEFAULT 'PREENCHA_O_SCHEMA';

USE CATALOG IDENTIFIER(workshop_catalog);
USE SCHEMA IDENTIFIER(workshop_schema);

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 1. Saúde atual dos ativos
-- MAGIC
-- MAGIC A tabela combina o último sinal, cadastro, unidade e alarmes abertos.

-- COMMAND ----------

CREATE OR REPLACE TABLE gold_asset_health_current
COMMENT 'Última condição observada e recomendação operacional por ativo sintético'
TBLPROPERTIES ('workshop.layer' = 'gold', 'workshop.contains_pii' = 'false')
AS
WITH latest_telemetry AS (
  SELECT * EXCEPT (rn)
  FROM (
    SELECT
      t.*,
      ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY event_ts DESC) AS rn
    FROM prepared_telemetry_5min t
  )
  WHERE rn = 1
),
open_alarms AS (
  SELECT asset_id, COUNT(*) AS active_alarms
  FROM prepared_alarms
  WHERE status = 'Aberto'
  GROUP BY asset_id
),
scored AS (
  SELECT
    t.event_ts,
    a.asset_id,
    a.asset_name,
    a.asset_type,
    a.site_id,
    s.site_name,
    s.operational_region,
    a.criticality,
    t.pressure_in_bar,
    t.pressure_out_bar,
    t.temperature_c,
    t.rotation_rpm,
    t.vibration_mm_s,
    t.flow_m3h,
    t.power_kw,
    t.sensor_status,
    COALESCE(o.active_alarms, 0) AS active_alarms,
    ROUND(t.flow_m3h / NULLIF(a.nominal_flow_m3h, 0), 3) AS flow_ratio,
    ROUND(t.power_kw / NULLIF(a.nominal_power_kw, 0), 3) AS power_ratio,
    GREATEST(
      0,
      100
        - CASE WHEN t.vibration_mm_s >= 7.1 THEN 35 WHEN t.vibration_mm_s >= 4.5 THEN 18 ELSE 0 END
        - CASE WHEN t.temperature_c >= 82 THEN 25 WHEN t.temperature_c >= 70 THEN 12 ELSE 0 END
        - CASE WHEN t.flow_m3h / NULLIF(a.nominal_flow_m3h, 0) < 0.60 THEN 25
               WHEN t.flow_m3h / NULLIF(a.nominal_flow_m3h, 0) < 0.78 THEN 12 ELSE 0 END
        - CASE WHEN t.power_kw / NULLIF(a.nominal_power_kw, 0) > 1.25 THEN 15 ELSE 0 END
        - LEAST(COALESCE(o.active_alarms, 0) * 4, 16)
    ) AS health_score
  FROM latest_telemetry t
  INNER JOIN prepared_assets a USING (asset_id)
  INNER JOIN prepared_sites s USING (site_id)
  LEFT JOIN open_alarms o USING (asset_id)
)
SELECT
  *,
  CASE
    WHEN health_score < 60 THEN 'Crítico'
    WHEN health_score < 80 THEN 'Atenção'
    ELSE 'Saudável'
  END AS health_status,
  CASE
    WHEN vibration_mm_s >= 7.1 AND flow_ratio < 0.78 THEN 'Inspecionar cavitação, sucção e alinhamento.'
    WHEN vibration_mm_s >= 7.1 THEN 'Inspecionar rolamentos e alinhamento em até 4 horas.'
    WHEN temperature_c >= 82 OR power_ratio > 1.25 THEN 'Reduzir carga e verificar refrigeração.'
    WHEN flow_ratio < 0.60 THEN 'Verificar obstrução, válvulas e perda de carga.'
    WHEN active_alarms > 0 THEN 'Triar alarmes ativos e confirmar condição em campo.'
    ELSE 'Manter monitoramento e plano preventivo.'
  END AS recommended_action
FROM scored;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 2. Tendência horária por ativo

-- COMMAND ----------

CREATE OR REPLACE TABLE gold_asset_health_hourly
COMMENT 'Tendência horária das variáveis operacionais por ativo sintético'
TBLPROPERTIES ('workshop.layer' = 'gold', 'workshop.contains_pii' = 'false')
AS
SELECT
  DATE_TRUNC('HOUR', t.event_ts) AS hour_ts,
  t.asset_id,
  a.site_id,
  s.site_name,
  s.operational_region,
  a.asset_type,
  a.criticality,
  ROUND(AVG(t.vibration_mm_s), 3) AS avg_vibration_mm_s,
  ROUND(AVG(t.temperature_c), 3) AS avg_temperature_c,
  ROUND(AVG(t.pressure_out_bar), 3) AS avg_pressure_out_bar,
  ROUND(AVG(t.flow_m3h), 3) AS avg_flow_m3h,
  ROUND(AVG(t.power_kw), 3) AS avg_power_kw,
  SUM(CASE WHEN t.sensor_status = 'SEM_SINAL' THEN 1 ELSE 0 END) AS missing_signal_points
FROM prepared_telemetry_5min t
INNER JOIN prepared_assets a USING (asset_id)
INNER JOIN prepared_sites s USING (site_id)
GROUP BY ALL;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 3. Operação diária por unidade

-- COMMAND ----------

CREATE OR REPLACE TABLE gold_site_operations_daily
COMMENT 'Indicadores operacionais diários por unidade sintética'
TBLPROPERTIES ('workshop.layer' = 'gold', 'workshop.contains_pii' = 'false')
AS
SELECT
  CAST(t.event_ts AS DATE) AS operation_date,
  a.site_id,
  s.site_name,
  s.operational_region,
  COUNT(DISTINCT t.asset_id) AS monitored_assets,
  COUNT(*) AS telemetry_points,
  ROUND(AVG(t.temperature_c), 2) AS avg_temperature_c,
  ROUND(AVG(t.vibration_mm_s), 2) AS avg_vibration_mm_s,
  ROUND(SUM(t.flow_m3h), 2) AS total_flow_m3,
  ROUND(AVG(t.power_kw), 2) AS avg_power_kw,
  SUM(CASE WHEN t.vibration_mm_s >= 4.5 OR t.temperature_c >= 70 THEN 1 ELSE 0 END) AS warning_points,
  SUM(CASE WHEN t.vibration_mm_s >= 7.1 OR t.temperature_c >= 82 THEN 1 ELSE 0 END) AS critical_points,
  ROUND(100 * AVG(CASE WHEN t.sensor_status <> 'SEM_SINAL' THEN 1.0 ELSE 0.0 END), 2) AS signal_availability_pct
FROM prepared_telemetry_5min t
INNER JOIN prepared_assets a USING (asset_id)
INNER JOIN prepared_sites s USING (site_id)
GROUP BY ALL;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 4. Impacto da manutenção

-- COMMAND ----------

CREATE OR REPLACE TABLE gold_maintenance_impact
COMMENT 'Ordens de serviço e variação de condição antes e depois da intervenção'
TBLPROPERTIES ('workshop.layer' = 'gold', 'workshop.contains_pii' = 'false')
AS
WITH measured AS (
  SELECT
    w.work_order_id,
    w.asset_id,
    w.site_id,
    w.created_ts,
    w.completed_ts,
    w.work_type,
    w.priority,
    w.status,
    w.downtime_hours,
    w.estimated_cost_brl,
    w.cause_code,
    AVG(CASE WHEN t.event_ts BETWEEN w.completed_ts - INTERVAL 6 HOURS AND w.completed_ts
             THEN t.vibration_mm_s END) AS vibration_before,
    AVG(CASE WHEN t.event_ts > w.completed_ts AND t.event_ts <= w.completed_ts + INTERVAL 6 HOURS
             THEN t.vibration_mm_s END) AS vibration_after,
    AVG(CASE WHEN t.event_ts BETWEEN w.completed_ts - INTERVAL 6 HOURS AND w.completed_ts
             THEN t.temperature_c END) AS temperature_before,
    AVG(CASE WHEN t.event_ts > w.completed_ts AND t.event_ts <= w.completed_ts + INTERVAL 6 HOURS
             THEN t.temperature_c END) AS temperature_after
  FROM prepared_work_orders w
  LEFT JOIN prepared_telemetry_5min t
    ON w.asset_id = t.asset_id
   AND w.completed_ts IS NOT NULL
   AND t.event_ts BETWEEN w.completed_ts - INTERVAL 6 HOURS AND w.completed_ts + INTERVAL 6 HOURS
  GROUP BY ALL
)
SELECT
  m.*,
  a.asset_name,
  a.asset_type,
  a.criticality,
  s.site_name,
  s.operational_region,
  ROUND(vibration_before - vibration_after, 3) AS vibration_reduction_mm_s,
  ROUND(temperature_before - temperature_after, 3) AS temperature_reduction_c
FROM measured m
INNER JOIN prepared_assets a ON m.asset_id = a.asset_id
INNER JOIN prepared_sites s ON m.site_id = s.site_id;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Verificação

-- COMMAND ----------

SELECT 'gold_asset_health_current' AS object_name, COUNT(*) AS row_count FROM gold_asset_health_current
UNION ALL
SELECT 'gold_asset_health_hourly', COUNT(*) FROM gold_asset_health_hourly
UNION ALL
SELECT 'gold_site_operations_daily', COUNT(*) FROM gold_site_operations_daily
UNION ALL
SELECT 'gold_maintenance_impact', COUNT(*) FROM gold_maintenance_impact;
