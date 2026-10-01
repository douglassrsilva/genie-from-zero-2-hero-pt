# Guia do participante

## Antes de começar

Você receberá do instrutor:

- URL do workspace;
- nome do catálogo e schema;
- SQL Warehouse a utilizar;
- grupo ou permissões para criar os objetos do laboratório.

Não gere dados e não instale dependências. As seis fontes sintéticas já estão
carregadas.

## 1. Gold

1. Abra `labs/01_create_gold.sql` no Git Folder.
2. Substitua `PREENCHA_O_CATALOGO` e `PREENCHA_O_SCHEMA` nas duas variáveis.
3. Execute uma célula por vez.
4. Confirme ao final:
   - 120 linhas em `gold_asset_health_current`;
   - 20.160 em `gold_asset_health_hourly`;
   - 210 em `gold_site_operations_daily`;
   - 240 em `gold_maintenance_impact`.
5. Localize o ativo com menor `health_score` e leia `recommended_action`.

## 2. Metric Views

1. Abra `labs/02_create_metric_views.sql` e preencha as mesmas variáveis.
2. Crie os dois objetos.
3. Execute as consultas com `MEASURE()`.
4. Confira se há pelo menos um ativo crítico e se todas as regiões aparecem.

## 3. Domain e Discover

Siga `DOMAIN_DISCOVER_GUIDE.md`. Crie o Domain e o Subdomain em rascunho e
adicione as quatro Gold e os dois Metric Views. Não publique até o instrutor
solicitar.

## 4. Genie Agent

Siga `GENIE_AGENT_GUIDE.md`. Depois de configurar as fontes e instruções,
pergunte:

> Quais regiões concentram mais ativos críticos e alarmes ativos?

Confira a resposta com a primeira consulta de validação do Metric View.

## 5. Dashboard

Siga `DASHBOARD_GUIDE.md`. Seu Dashboard deve ter quatro KPIs, dois gráficos,
uma tabela operacional e filtros de região/unidade.

## 6. App

Abra a App fornecida, aplique os quatro filtros e selecione um ativo crítico.
Modifique um texto, título ou coluna conforme orientação. Não adicione token,
host ou ID no código.

## 7. Page, Genie One e Ontology

Finalize a Page, publique com o instrutor e valide a mesma pergunta pelo Genie
One. Use `GENIE_ONE_ONTOLOGY_GUIDE.md` para reconhecer o contexto explícito e
inferido; não procure um botão “Criar Ontology”.

## Desafio pós-workshop

Modernize a App mantendo:

- os quatro filtros funcionais;
- os contratos das duas Gold consumidas;
- uma indicação visual acessível de criticidade;
- nenhuma credencial ou nome de ambiente no código;
- uma evidência de validação antes/depois.

Extensões opcionais: comparação entre dois ativos, janela temporal, anotação de
alarmes, deep link para o Dashboard ou incorporação de uma conversa com o Agent.
