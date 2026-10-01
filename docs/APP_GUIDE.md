# Databricks App — execução e desafio

A App em `apps/asset-health/` é intencionalmente simples. Ela consome
`gold_asset_health_current` e `gold_asset_health_hourly` com catálogo, schema e
Warehouse fornecidos em tempo de deploy.

## Preparação do instrutor

Valide localmente:

```bash
cd apps/asset-health
uv run --with-requirements requirements-dev.txt pytest -q
uv run --with-requirements requirements-dev.txt ruff check .
```

Para usar o Bundle, forneça variáveis sem editar arquivos:

```bash
databricks bundle validate -t dev \
  --var="catalog=<CATALOGO>,schema=<SCHEMA>,warehouse_id=<WAREHOUSE_ID>"
databricks bundle deploy -t dev \
  --var="catalog=<CATALOGO>,schema=<SCHEMA>,warehouse_id=<WAREHOUSE_ID>"
```

O Bundle associa as duas tabelas com `SELECT` e o Warehouse com `CAN USE`. A
identidade de serviço da App recebe os acessos necessários; não use tokens.

## Atividade ao vivo

1. Abra a App e confira os quatro KPIs.
2. Filtre região, unidade, criticidade e ativo.
3. Escolha um ativo crítico e compare a tendência com a ação recomendada.
4. No Git Folder, altere o título/texto ou adicione uma coluna existente à
   tabela priorizada.
5. Faça deploy novamente e verifique que os filtros continuam funcionando.

## Desafio de modernização

Entregável mínimo:

- hierarquia visual clara e responsiva;
- criticidade acessível, não dependente apenas de cor;
- comparação antes/depois ou entre dois ativos;
- link contextual para Dashboard ou Agent;
- estados de carregamento, vazio e erro legíveis;
- nenhuma credencial ou identificação do ambiente no código;
- evidência de teste dos filtros e contrato Gold.

Extensões: anotações de alarmes na série, seletor de janela, ação simulada com
confirmação, incorporação do Agent ou visão para dispositivos móveis.
