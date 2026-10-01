# Validação de nomenclatura e disponibilidade

Verificado em documentação oficial em **01/10/2026**. Revalidar antes de cada
turma, pois previews e rótulos de interface mudam.

| Item | Decisão adotada |
|---|---|
| Metric Views | YAML 1.1, com `display_name` e `synonyms`; metadados semânticos recentes exigem SQL Warehouse ou DBR 17.3+ |
| Genie Agent | nome atual; “Genie Space” é nomenclatura anterior e ainda pode aparecer em APIs/configurações |
| Genie One | nome atual; “Databricks One” é nomenclatura anterior |
| Domains e Discover | Public Preview |
| Pages | Beta |
| Genie Ontology | Public Preview; contexto composto, não objeto criado por botão/API/DDL |
| Databricks Apps | App Streamlit com identidade de serviço e recursos associados |

Referências:

- [Metric Views](https://docs.databricks.com/uc-semantics/metric-views/)
- [Sintaxe de Metric Views](https://docs.databricks.com/aws/en/metric-views/data-modeling/syntax)
- [AI/BI Genie](https://docs.databricks.com/aws/en/genie/)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/dashboards/)
- [Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [Recursos de Apps em Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/resources#app)
- [Discover](https://docs.databricks.com/aws/en/discover/)

## Limitação deliberada

Não há automação de criação de Domain/Page/Ontology neste repositório. Domain e
Page são atividades de console; Ontology não possui etapa de criação separada.
Agent e Dashboard são construídos na interface para preservar o objetivo
didático, com instruções e SQL versionados para reprodutibilidade.
