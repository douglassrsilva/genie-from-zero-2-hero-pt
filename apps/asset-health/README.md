# App de saúde de ativos

Aplicação Streamlit básica e interna para o workshop **Genie do Zero ao Herói**.
Ela usa os mesmos ativos semânticos da jornada de consumo e foi mantida simples
de propósito: o desafio dos participantes é modernizar a experiência.

## O que a aplicação entrega

- filtros de região, estação, criticidade e ativo;
- quatro KPIs operacionais;
- tabela de ativos priorizados;
- tendência horária de vibração e temperatura;
- recomendação de ação baseada nas Gold do workshop.

## Contrato de dados

No Databricks, a aplicação consulta:

- `gold_asset_health_current`;
- `gold_asset_health_hourly`.

Catálogo, schema e Warehouse não são fixados no código. O ambiente precisa
fornecer:

```text
UTILITY_CATALOG
UTILITY_SCHEMA
DATABRICKS_WAREHOUSE_ID
```

O recurso de SQL Warehouse associado ao App deve usar a chave
`sql-warehouse`, como definido em `app.yaml`. Adicione `UTILITY_CATALOG` e
`UTILITY_SCHEMA` durante o deploy ou por automação do Bundle.

A identidade de serviço da App precisa de:

- `CAN USE` no SQL Warehouse;
- `USE CATALOG` no catálogo;
- `USE SCHEMA` no schema;
- `SELECT` nas duas tabelas Gold.

## Execução local sem credenciais

Sem as três variáveis remotas, a aplicação lê Parquet em
`../../data/prepared`. Ela aceita as Gold prontas:

```text
gold_asset_health_current.parquet
gold_asset_health_hourly.parquet
```

Se elas não existirem, a contingência pode derivar uma amostra das fontes
`dim_assets`, `dim_sites`, `fact_telemetry_5min` e, opcionalmente,
`fact_alarms`. Para apontar para outra pasta, use `UTILITY_DATA_DIR`.

```bash
cd apps/asset-health
uv run --with-requirements requirements.txt streamlit run app.py
```

Esse modo não lê perfil, token ou arquivo de autenticação. Para testar o acesso
remoto fora de Databricks Apps, defina as três variáveis e use a autenticação
padrão já configurada do Databricks SDK.

## Testes

```bash
cd apps/asset-health
uv run --with-requirements requirements-dev.txt pytest -q
uv run --with-requirements requirements-dev.txt ruff check .
```

Os testes constroem Parquet temporário e não gravam dados do ambiente no
repositório.

## Exercício ao vivo

1. Abra `app.py` e localize os quatro KPIs.
2. Altere o título e o texto introdutório.
3. Adicione uma informação à tabela priorizada.
4. Escolha uma melhoria visual ou de navegação.
5. Execute novamente e confirme que os filtros continuam funcionando.

O deploy não faz parte destes arquivos. O recurso Databricks App e suas
permissões devem estar preparados antes do workshop.

