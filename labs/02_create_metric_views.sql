-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Laboratório 2 — Metric Views
-- MAGIC
-- MAGIC Requisito: SQL Warehouse compatível ou Databricks Runtime 17.3+ para os
-- MAGIC metadados semânticos usados no YAML 1.1.

-- COMMAND ----------

DECLARE OR REPLACE VARIABLE workshop_catalog STRING DEFAULT 'PREENCHA_O_CATALOGO';
DECLARE OR REPLACE VARIABLE workshop_schema STRING DEFAULT 'PREENCHA_O_SCHEMA';

USE CATALOG IDENTIFIER(workshop_catalog);
USE SCHEMA IDENTIFIER(workshop_schema);

-- COMMAND ----------

CREATE OR REPLACE VIEW mv_operational_health
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: Camada semântica governada para saúde operacional de ativos
source: gold_asset_health_current
dimensions:
  - name: operational_region
    display_name: Região operacional
    expr: operational_region
    synonyms: [região, área, regional]
  - name: site_name
    display_name: Unidade operacional
    expr: site_name
    synonyms: [unidade, estação, planta]
  - name: asset_type
    display_name: Tipo de ativo
    expr: asset_type
    synonyms: [equipamento, classe do ativo]
  - name: criticality
    display_name: Criticidade
    expr: criticality
    synonyms: [prioridade, importância]
  - name: health_status
    display_name: Estado de saúde
    expr: health_status
    synonyms: [condição, status, severidade]
  - name: event_date
    display_name: Data da leitura
    expr: CAST(event_ts AS DATE)
    synonyms: [data, dia]
measures:
  - name: asset_count
    display_name: Quantidade de ativos
    expr: COUNT(DISTINCT asset_id)
    synonyms: [total de ativos, equipamentos]
  - name: critical_asset_count
    display_name: Ativos críticos
    expr: COUNT(DISTINCT CASE WHEN health_status = 'Crítico' THEN asset_id END)
    synonyms: [ativos em risco, equipamentos críticos]
  - name: average_health_score
    display_name: Índice médio de saúde
    expr: AVG(health_score)
    synonyms: [saúde média, score médio]
    format:
      type: number
      decimal_places:
        type: exact
        places: 1
  - name: active_alarm_count
    display_name: Alarmes ativos
    expr: SUM(active_alarms)
    synonyms: [alarmes abertos, total de alarmes]
  - name: average_power_kw
    display_name: Potência média
    expr: AVG(power_kw)
    synonyms: [consumo médio, carga média]
    format:
      type: number
      decimal_places:
        type: exact
        places: 1
$$;

-- COMMAND ----------

CREATE OR REPLACE VIEW mv_maintenance_reliability
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: Camada semântica governada para manutenção e confiabilidade
source: gold_maintenance_impact
dimensions:
  - name: operational_region
    display_name: Região operacional
    expr: operational_region
    synonyms: [região, área, regional]
  - name: site_name
    display_name: Unidade operacional
    expr: site_name
    synonyms: [unidade, estação, planta]
  - name: asset_type
    display_name: Tipo de ativo
    expr: asset_type
    synonyms: [equipamento, classe do ativo]
  - name: work_type
    display_name: Tipo de manutenção
    expr: work_type
    synonyms: [intervenção, serviço]
  - name: order_status
    display_name: Situação da ordem
    expr: status
    synonyms: [status da OS, situação]
  - name: created_date
    display_name: Data de abertura
    expr: CAST(created_ts AS DATE)
    synonyms: [data, abertura]
measures:
  - name: work_order_count
    display_name: Quantidade de ordens
    expr: COUNT(DISTINCT work_order_id)
    synonyms: [total de OS, intervenções]
  - name: maintenance_cost_brl
    display_name: Custo estimado de manutenção
    expr: SUM(estimated_cost_brl)
    synonyms: [custo, gasto de manutenção]
    format:
      type: currency
      currency_code: BRL
      decimal_places:
        type: exact
        places: 2
  - name: downtime_hours
    display_name: Horas de indisponibilidade
    expr: SUM(downtime_hours)
    synonyms: [parada, indisponibilidade]
    format:
      type: number
      decimal_places:
        type: exact
        places: 1
  - name: average_vibration_reduction
    display_name: Redução média de vibração
    expr: AVG(vibration_reduction_mm_s)
    synonyms: [melhora de vibração, efeito da manutenção]
    format:
      type: number
      decimal_places:
        type: exact
        places: 2
$$;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Verifique as métricas

-- COMMAND ----------

SELECT
  operational_region,
  MEASURE(asset_count) AS asset_count,
  MEASURE(critical_asset_count) AS critical_asset_count,
  ROUND(MEASURE(average_health_score), 1) AS average_health_score,
  MEASURE(active_alarm_count) AS active_alarm_count
FROM mv_operational_health
GROUP BY operational_region
ORDER BY critical_asset_count DESC;

-- COMMAND ----------

SELECT
  work_type,
  MEASURE(work_order_count) AS work_order_count,
  ROUND(MEASURE(maintenance_cost_brl), 2) AS maintenance_cost_brl,
  ROUND(MEASURE(downtime_hours), 1) AS downtime_hours
FROM mv_maintenance_reliability
GROUP BY work_type
ORDER BY maintenance_cost_brl DESC;
