# Guia rápido da demonstração

## Antes da sessão

1. Importe ou conecte este repositório a um Git Folder do workspace.
2. Defina catálogo e schema de laboratório; não altere os arquivos para inserir
   nomes do ambiente.
3. Execute `labs/00_load_prepared.py` com os widgets preenchidos e confirme as
   seis linhas `OK`.
4. Execute os três SQL de `labs/` uma vez em um schema de ensaio.
5. Prepare um SQL Warehouse com auto-stop curto e aqueça-o 10 minutos antes.
6. Confirme que cada participante pode criar/consultar objetos no namespace.
7. Confirme a habilitação de Domains, Pages, Genie Agent, AI/BI Dashboard,
   Databricks Apps e Genie One.
8. Deixe uma App, um Agent e um Dashboard de contingência prontos, porém não
   publicados na Page principal.

## Ordem da demonstração

1. Use a apresentação fornecida para os 20 minutos iniciais.
2. Mostre a saída do `00_load_prepared.py` e abra `01_create_gold.sql`; os
   participantes editam somente duas variáveis e executam o preflight.
3. Abra `02_create_metric_views.sql`; explique dimensão, medida e sinônimo.
4. Crie Domain/Subdomain em rascunho, sem publicar ainda.
5. Crie o Genie Agent e cole `config/genie_agent_instructions.md`.
6. Construa o Dashboard com `labs/03_validation_queries.sql`.
7. Abra a App preparada e faça uma alteração pequena ao vivo.
8. Crie a Page, adicione Agent/Dashboard/App/Metric Views e publique o Domain.
9. Troque para a experiência Genie One e refaça uma pergunta conhecida.
10. Mostre como os ativos anteriores formam a Ontology; não existe um objeto
    “Ontology” criado por botão, DDL ou API.

## Artefatos de contingência

- Parquet preparado e manifesto: `data/prepared/`;
- validação SQL pronta: `labs/03_validation_queries.sql`;
- texto do Agent: `config/genie_agent_instructions.md`;
- texto do Domain/Page: `config/domain_page_content.md`;
- App com fallback local: `apps/asset-health/`.

Consulte `docs/INSTRUCTOR_RUNBOOK.md` para marcações de tempo, verificações e
plano B de cada módulo.
