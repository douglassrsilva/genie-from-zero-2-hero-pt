# Runbook do instrutor

## Objetivo e público

Workshop para analistas, engenheiros, líderes operacionais e profissionais de
dados iniciantes em Databricks. Em três horas, a turma transforma dados de
telemetria já preparados em produtos de consumo governados e uma experiência
operacional integrada.

O caso é fictício e não representa uma empresa específica. A turma monitora
30 unidades e 120 ativos com pressão, temperatura, rotação, vibração, vazão,
potência, alarmes e ordens de serviço.

## Premissas

- turma de até 24 pessoas, preferencialmente em duplas;
- SQL básico, sem pré-requisito de Python ou Spark;
- workspace com Unity Catalog e SQL Warehouse;
- catálogo/schema definidos pelo instrutor e nunca gravados no repositório;
- dados `prepared_*` carregados antes da sessão;
- recursos de preview habilitados e testados na região usada;
- uma cópia de contingência de Agent, Dashboard e App criada previamente.

## Preparação técnica — fora das 180 minutos

### Permissões mínimas

| Atividade | Permissão |
|---|---|
| Consultar fontes | `USE CATALOG`, `USE SCHEMA`, `SELECT` em `prepared_*` |
| Criar Gold e Metric Views | `CREATE TABLE`, `CREATE MATERIALIZED VIEW`/`CREATE VIEW` conforme política do workspace |
| SQL Warehouse | `CAN USE` |
| Domain/Page | direito de criar/editar Domain e publicar ativos no Discover |
| Genie Agent | `CREATE`/`CAN EDIT` do Agent e `SELECT` nas fontes |
| Dashboard | direito de criar Dashboard e executar datasets |
| Databricks App | direito de criar/deploy e associar recursos |
| Genie One | habilitação do produto e acesso aos ativos publicados |

Não conceda privilégios administrativos amplos à turma. Se a política não
permitir criação, use objetos por dupla previamente criados e concentre a
prática em consulta/configuração.

### Checklist de ensaio

1. Conecte o repositório a um Git Folder.
2. Execute `labs/00_load_prepared.py` com catálogo/schema e deixe a saída das
   seis tabelas visível para a turma.
3. Confirme as contagens 30, 120, 241.920, 480, 240 e 18.
4. Rode `labs/01_create_gold.sql` e `labs/02_create_metric_views.sql` completos.
5. Rode `labs/03_validation_queries.sql` e confirme 120 ativos distintos.
6. Crie uma versão de contingência do Agent, Dashboard e App.
7. Confirme que o Domain permanece em rascunho para a parte inicial.
8. Teste publicação, busca no Discover e acesso pelo Genie One com um usuário
   que tenha o mesmo perfil de permissões da turma.
9. Aqueça o Warehouse e abra todas as abas dez minutos antes.

## Condução Tell–Show–Tell

### 1. Plataforma e jornada de consumo — 20 minutos

**Tell — 15 min:** use a apresentação fornecida. Posicione Lakehouse, Unity
Catalog, AI/BI, Agent Bricks/Genie e Apps. Explique que o workshop começa em
dados preparados e se concentra em transformar dados em uma experiência de
decisão. Mostre a jornada integrada, sem detalhar geração ou ingestão.

**Show — não aplicável:** este é o único módulo predominantemente conceitual.

**Tell final — 5 min:** confirme o objetivo: “ao final, uma pergunta de negócio
terá a mesma definição no SQL, Dashboard, Agent, App, Discover e Genie One”.

**Verificação:** participantes conseguem descrever a diferença entre tabela
Gold, Metric View e experiência de consumo.

**Contingência:** se a apresentação falhar, use o diagrama do README e avance
no minuto 20.

### 2. Camada Gold — 18 minutos

**Tell — 3 min:** Gold é o contrato estável e consumível. Mostre as seis fontes
prepared no Catalog Explorer e explique a granularidade.

**Show/prática — 13 min:** mostre a carga concluída em `labs/00_load_prepared.py`
e abra `labs/01_create_gold.sql`. Cada dupla altera as duas variáveis, executa o
preflight e depois os quatro blocos. O instrutor chama atenção para o último
evento, score, tendência horária, operação diária e impacto de manutenção.

**Tell final — 2 min:** confira a saída: 120 linhas em
`gold_asset_health_current`; 20.160 em `gold_asset_health_hourly`; 210 em
`gold_site_operations_daily`; 240 em `gold_maintenance_impact`.

**Artefato:** quatro tabelas Gold managed.

**Contingência:** em caso de permissão ou tempo, dê `SELECT` nas Gold de
contingência. Não tente reconfigurar Unity Catalog durante a sessão.

### 3. Metric Views — 20 minutos

**Tell — 3 min:** separe dimensão, medida e sinônimo. Mostre por que a lógica de
“ativos críticos” não deve ser reescrita em cada consumidor.

**Show/prática — 15 min:** execute `labs/02_create_metric_views.sql` em um SQL
Warehouse compatível. Cada dupla cria `mv_operational_health` e
`mv_maintenance_reliability`, depois executa as duas consultas com `MEASURE()`.
Peça a uma dupla para trocar “região” por um sinônimo no Agent mais tarde.

**Tell final — 2 min:** compare a consulta da Metric View com uma agregação
manual. Reforce definição única e governada.

**Artefato:** dois Metric Views YAML 1.1.

**Contingência:** se o runtime não suportar metadados 1.1, use os Metric Views
pré-criados. Não remova sinônimos ao vivo nem converta para view SQL comum.

### 4. Domain, Subdomain e Discover — 15 minutos

**Tell — 3 min:** Domain organiza responsabilidade e contexto; Subdomain reduz
o escopo; Discover é a experiência de descoberta. A Page será publicada apenas
depois dos consumidores existirem.

**Show/prática — 10 min:** siga `DOMAIN_DISCOVER_GUIDE.md`. Crie o Domain
“Operações Industriais” e o Subdomain “Saúde de Ativos” em rascunho. Adicione
as quatro Gold e os dois Metric Views ao Subdomain. Não publique ainda.

**Tell final — 2 min:** abra a prévia e identifique proprietário, descrição e
ativos.

**Artefato:** estrutura de Domain/Subdomain em rascunho.

**Contingência:** se Domains não estiver habilitado, use uma captura do ensaio e
registre a estrutura em `config/domain_page_content.md`; prossiga com o Agent.

### 5. Genie Agent — 22 minutos

**Tell — 4 min:** Genie Agent é o nome atual do antigo Genie Space. Explique a
relação entre fontes autorizadas, instruções, exemplos SQL e benchmark.

**Show/prática — 16 min:** siga `GENIE_AGENT_GUIDE.md`. Adicione os dois Metric
Views e as Gold de tendência/diária, cole as instruções e teste duas perguntas.
Mostre a consulta gerada, valide números contra SQL e corrija uma instrução.

**Tell final — 2 min:** uma boa resposta depende de dados, semântica, contexto
e avaliação; não apenas do modelo.

**Artefato:** Agent “Saúde de Ativos” validado.

**Contingência:** se Agent estiver indisponível, execute as consultas esperadas
de `03_validation_queries.sql` e mostre a gravação/captura do ensaio.

### 6. AI/BI Dashboard — 20 minutos

**Tell — 3 min:** o Dashboard conta a história recorrente; o Agent responde à
pergunta exploratória. Ambos devem compartilhar as mesmas métricas.

**Show/prática — 15 min:** siga `DASHBOARD_GUIDE.md`. Crie quatro KPIs, barra de
críticos por região, tendência de vibração/temperatura e tabela de prioridade.
Adicione filtros de região e unidade; valide um KPI contra a Metric View.

**Tell final — 2 min:** peça à turma para apontar a próxima ação operacional,
não apenas o maior número.

**Artefato:** Dashboard em rascunho.

**Contingência:** use o Dashboard de contingência e peça apenas a alteração de
um filtro/título. Se o Warehouse atrasar, mostre resultados em cache.

### 7. Databricks App — 20 minutos

**Tell — 3 min:** App atende um fluxo de decisão específico; não substitui o
Dashboard. A versão base é propositalmente simples.

**Show/prática — 15 min:** abra a App pré-deployada. Aplique filtros, selecione
um ativo crítico e relacione KPI, tendência e recomendação. Altere título/texto
ou uma coluna da lista no Git Folder, redeploy e confirme a mudança.

**Tell final — 2 min:** discuta que identidade de serviço e recursos associados
evitam credenciais no código.

**Artefato:** App básica adaptada e funcional.

**Contingência:** rode o fallback local antes da sessão e use sua captura ou
abra a App de contingência. Não configure autenticação ao vivo.

### 8. Page e publicação do Domain — 15 minutos

**Tell — 3 min:** Page transforma ativos isolados em uma porta de entrada
curada. Publicação é um ato de governança.

**Show/prática — 10 min:** crie a Page “Central de Saúde Operacional” com o
texto de `config/domain_page_content.md`. Adicione Metric Views, Agent,
Dashboard e App. Faça prévia, revise permissões e publique Domain/Page.

**Tell final — 2 min:** abra o Discover como consumidor e confirme que os
quatro caminhos estão acessíveis.

**Artefato:** Page publicada no Domain.

**Contingência:** mantenha o Domain em rascunho e demonstre a Page de
contingência se a publicação estiver bloqueada.

### 9. Genie One — 15 minutos

**Tell — 3 min:** Genie One é a experiência de consumo unificada e governada;
não é um novo pipeline nem uma cópia dos dados.

**Show/prática — 10 min:** entre como usuário consumidor, encontre a Page,
abra o Agent e refaça “quais regiões concentram mais ativos críticos?”. Navegue
da resposta para o Dashboard e a App.

**Tell final — 2 min:** destaque que permissões do Unity Catalog continuam
valendo na experiência simplificada.

**Artefato:** jornada de consumo validada.

**Contingência:** se Genie One não estiver habilitado, execute o mesmo roteiro
no Discover padrão e explique a equivalência de ativos, sem fingir a UI.

### 10. Genie Ontology — 10 minutos

**Tell — 3 min:** Ontology não é um objeto criado por botão, DDL ou API. Ela é
formada por contexto explícito e contexto inferido.

**Show/prática — 6 min:** mostre o contexto explícito dos Metric Views,
Domain/Page, descrições e instruções. Depois peça ao Agent para explicar “ativo
crítico” e para correlacionar saúde com manutenção. Aponte a reutilização de
relações e termos.

**Tell final — 1 min:** resuma: semântica + organização + uso = contexto útil
para a inteligência.

**Artefato:** evidência da Ontology aplicada; nenhum objeto adicional.

**Contingência:** use as duas consultas validadas e a Page para narrar a mesma
composição de contexto.

### 11. Fechamento e margem — 5 minutos

Reserve o bloco para dúvidas, atraso pequeno ou para lançar o desafio:
modernizar a App sem quebrar filtros, contrato Gold ou segurança. Se não houver
atrasos, peça a cada dupla para escolher uma melhoria e registrar como faria a
validação.

## Encerramento de recursos

- pare o SQL Warehouse ou confirme auto-stop;
- interrompa a App de ensaio se ela não for reutilizada;
- remova o schema descartável do dry run, nunca o schema compartilhado sem
  confirmação explícita;
- preserve Dashboard, Agent, Domain e Page da turma conforme política interna;
- revise custo e permissões de objetos publicados.
