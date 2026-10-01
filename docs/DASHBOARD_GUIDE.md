# AI/BI Dashboard — Central de Saúde Operacional

## Datasets

Crie os datasets abaixo em um AI/BI Dashboard novo, usando o Warehouse do
workshop.

### `kpis_operacionais`

```sql
SELECT
  MEASURE(asset_count) AS total_assets,
  MEASURE(critical_asset_count) AS critical_assets,
  ROUND(MEASURE(average_health_score), 1) AS average_health_score,
  MEASURE(active_alarm_count) AS active_alarms
FROM <CATALOGO>.<SCHEMA>.mv_operational_health
```

### `criticos_por_regiao`

```sql
SELECT
  operational_region,
  MEASURE(critical_asset_count) AS critical_assets,
  MEASURE(active_alarm_count) AS active_alarms
FROM <CATALOGO>.<SCHEMA>.mv_operational_health
GROUP BY operational_region
```

### `tendencia_ativo_prioritario`

Use a consulta de tendência em `labs/03_validation_queries.sql`. Ela escolhe o
ativo de pior score sem gravar um ID no Dashboard.

### `fila_operacional`

Use a consulta de ranking em `labs/03_validation_queries.sql`.

## Canvas

1. Título: **Central de Saúde Operacional**.
2. Primeira linha: quatro contadores — ativos monitorados, ativos críticos,
   índice médio e alarmes ativos.
3. Segunda linha: barras de críticos por região e série temporal com duas
   linhas, vibração e temperatura.
4. Terceira linha: tabela de prioridade com ação recomendada.
5. Adicione filtros de `operational_region` e `site_name` aos datasets que
   expõem essas colunas.
6. Use cores acessíveis e texto além da cor para indicar criticidade.
7. Valide o total de críticos contra o Metric View antes de publicar.

## Critério de sucesso

- quatro KPIs carregam sem erro;
- filtros alteram os visuais relacionados;
- a tendência tem 168 horas para o ativo escolhido;
- a tabela começa pelo menor `health_score`;
- nenhum dataset possui catálogo/schema pessoal gravado no repositório.

## Contingência

Se a turma não puder criar Dashboard, forneça uma cópia editável do modelo de
ensaio. Cada dupla deve alterar título, filtro e um visual, e depois validar um
KPI.
