# Dados preparados

Dados sintéticos de uma operação industrial fictícia. Eles representam 30
unidades, 120 ativos e sete dias de telemetria em intervalos de cinco minutos.

| Arquivo | Granularidade | Uso |
|---|---|---|
| `sites.parquet` | uma linha por unidade | geografia operacional |
| `assets.parquet` | uma linha por ativo | cadastro e valores nominais |
| `telemetry_5min.parquet` | ativo a cada cinco minutos | condição operacional |
| `alarms.parquet` | uma linha por alarme | eventos e severidade |
| `work_orders.parquet` | uma linha por ordem | manutenção e indisponibilidade |
| `operating_thresholds.parquet` | tipo de ativo e métrica | limites operacionais |

Os cenários de cavitação, desgaste de rolamento, obstrução e sobrecarga são
determinísticos. Não há dados pessoais ou informações de empresas reais.
