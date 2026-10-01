-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Validações e consultas para o Dashboard

-- COMMAND ----------

DECLARE OR REPLACE VARIABLE workshop_catalog STRING DEFAULT 'PREENCHA_O_CATALOGO';
DECLARE OR REPLACE VARIABLE workshop_schema STRING DEFAULT 'PREENCHA_O_SCHEMA';
USE CATALOG IDENTIFIER(workshop_catalog);
USE SCHEMA IDENTIFIER(workshop_schema);

-- COMMAND ----------

-- Deve retornar 120 ativos, sem duplicidade.
SELECT
  COUNT(*) AS rows,
  COUNT(DISTINCT asset_id) AS distinct_assets,
  SUM(CASE WHEN health_score BETWEEN 0 AND 100 THEN 0 ELSE 1 END) AS invalid_scores
FROM gold_asset_health_current;

-- COMMAND ----------

-- Ranking para a tabela operacional do Dashboard.
SELECT
  asset_id,
  asset_name,
  site_name,
  operational_region,
  criticality,
  health_status,
  health_score,
  active_alarms,
  recommended_action
FROM gold_asset_health_current
ORDER BY health_score ASC, active_alarms DESC
LIMIT 20;

-- COMMAND ----------

-- Tendência de sete dias para um ativo crítico, escolhida sem ID fixo.
WITH target AS (
  SELECT asset_id
  FROM gold_asset_health_current
  ORDER BY health_score ASC
  LIMIT 1
)
SELECT
  h.hour_ts,
  h.asset_id,
  h.avg_vibration_mm_s,
  h.avg_temperature_c
FROM gold_asset_health_hourly h
INNER JOIN target t USING (asset_id)
ORDER BY hour_ts;

-- COMMAND ----------

-- Fonte opcional para um mapa de calor por unidade e dia.
SELECT
  operation_date,
  site_name,
  operational_region,
  critical_points,
  warning_points,
  signal_availability_pct
FROM gold_site_operations_daily
ORDER BY operation_date, critical_points DESC;
