# Genie do Zero ao Herói — Utilities

Workshop mão na massa, em português, centrado na camada de consumo da
Databricks Data Intelligence Platform. O caso acompanha a saúde de 120 ativos
industriais por meio de pressão, temperatura, rotação, vibração, vazão e
potência.

Os dados sintéticos já estão prontos. Nenhum minuto da sessão é usado para
gerá-los: o participante começa criando a Gold e evolui a mesma solução por
Metric Views, Discover, Genie Agent, AI/BI Dashboard, Databricks App, Genie One
e Genie Ontology.

## Resultado da jornada

```text
Parquet preparado → tabelas prepared_* → quatro Gold → dois Metric Views
                                              │
                      ┌───────────────────────┼──────────────────────┐
                      ▼                       ▼                      ▼
               Genie Agent          AI/BI Dashboard       Databricks App
                      └───────────────────────┬──────────────────────┘
                                              ▼
                          Domain + Subdomain + Page → Discover
                                              ▼
                                   Genie One + Ontology
```

Ao final, o ambiente contém:

- quatro tabelas Gold de saúde, tendência, operação e manutenção;
- dois Metric Views com nomes de negócio e sinônimos;
- um Domain, um Subdomain e uma Page no Discover;
- um Genie Agent com instruções e perguntas validadas;
- um AI/BI Dashboard operacional;
- uma App Streamlit simples, pronta para o desafio de modernização;
- uma demonstração do consumo no Genie One e da formação da Ontology.

## Agenda — 180 minutos

| Horário | Módulo | Duração | Tell | Show/prática | Tell final |
|---|---|---:|---:|---:|---:|
| 09:00 | Plataforma e jornada de consumo | 20 min | 15 | 0 | 5 |
| 09:20 | Construção da Gold | 18 min | 3 | 13 | 2 |
| 09:38 | Metric Views | 20 min | 3 | 15 | 2 |
| 09:58 | Domain, Subdomain e Discover | 15 min | 3 | 10 | 2 |
| 10:13 | Genie Agent | 22 min | 4 | 16 | 2 |
| 10:35 | AI/BI Dashboard | 20 min | 3 | 15 | 2 |
| 10:55 | Databricks App | 20 min | 3 | 15 | 2 |
| 11:15 | Page e publicação do Domain | 15 min | 3 | 10 | 2 |
| 11:30 | Genie One | 15 min | 3 | 10 | 2 |
| 11:45 | Genie Ontology | 10 min | 3 | 6 | 1 |
| 11:55 | Fechamento, dúvidas e margem | 5 min | 3 | 0 | 2 |
| | **Total** | **180 min** | **46** | **110** | **24** |

O tempo de demonstração e prática é de 110 minutos, ou 61,1% da sessão. A
última faixa absorve dúvidas e pequenos atrasos; cada módulo também possui uma
contingência no runbook.

## Comece aqui

1. Instrutor: execute o [checklist e runbook](docs/INSTRUCTOR_RUNBOOK.md).
2. Participante: use o [guia de laboratório](docs/PARTICIPANT_GUIDE.md).
3. Crie as Gold com [`labs/01_create_gold.sql`](labs/01_create_gold.sql).
4. Crie a semântica com [`labs/02_create_metric_views.sql`](labs/02_create_metric_views.sql).
5. Use os guias de [Discover](docs/DOMAIN_DISCOVER_GUIDE.md),
   [Genie](docs/GENIE_AGENT_GUIDE.md), [Dashboard](docs/DASHBOARD_GUIDE.md) e
   [Genie One/Ontology](docs/GENIE_ONE_ONTOLOGY_GUIDE.md).
6. Adapte a [App de saúde de ativos](apps/asset-health/README.md).

## Pré-requisitos do participante

- saber navegar em um browser;
- entender `SELECT`, `WHERE`, `GROUP BY` e agregações SQL simples;
- reconhecer tabela, coluna e medida de negócio;
- não é necessário conhecer Python, Spark ou administração Databricks.

O instrutor deve provisionar conta, workspace, permissões, SQL Warehouse e
recursos em preview antes da sessão. O repositório não contém credenciais, IDs
de Warehouse, nomes de catálogo/schema ou dados pessoais.

## Disponibilidade dos produtos

A nomenclatura e a disponibilidade foram verificadas em 01/10/2026. Genie
Agent é o nome atual do antigo Genie Space; Genie One é o nome atual do antigo
Databricks One. Domains/Discover estão em Public Preview, Pages em Beta e
Genie Ontology em Public Preview. Esses recursos podem exigir habilitação ou
não estar presentes em toda região/edição. Consulte
[`docs/PRODUCT_VALIDATION.md`](docs/PRODUCT_VALIDATION.md) antes de cada turma.
