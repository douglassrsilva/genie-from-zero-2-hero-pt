# Genie Agent de Saúde de Ativos

Genie Agent é o nome atual do recurso anteriormente chamado Genie Space. O
exercício cria um Agent analítico governado; não cria um agente autônomo que
executa manutenção.

## Criação

1. Abra **Genie** e selecione **New agent**.
2. Nomeie como **Saúde de Ativos**.
3. Conecte o SQL Warehouse indicado pelo instrutor.
4. Adicione as fontes:
   - `mv_operational_health`;
   - `mv_maintenance_reliability`;
   - `gold_asset_health_hourly`;
   - `gold_site_operations_daily`.
5. Em **Instructions**, cole `config/genie_agent_instructions.md`.
6. Salve e aguarde a validação das fontes.

## Duas perguntas em modo chat

1. **Quais regiões concentram mais ativos críticos e alarmes ativos?**
2. **Mostre os cinco ativos que precisam de atenção primeiro e explique o
   motivo com base nas leituras observadas.**

Para cada uma:

1. abra a consulta gerada;
2. confirme fonte, filtros e medidas;
3. compare o total com `labs/02_create_metric_views.sql` ou
   `labs/03_validation_queries.sql`;
4. marque a resposta como correta/incorreta conforme a UI disponível;
5. ajuste uma instrução apenas se houver diferença reproduzível.

## Duas perguntas para pesquisa aprofundada

Use o modo de pesquisa aprofundada apenas se ele estiver habilitado no
workspace. Ele precisa sintetizar várias evidências, não apenas retornar uma
lista.

1. **Investigue quais unidades apresentam um padrão compatível com degradação
   mecânica. Use vibração, temperatura, alarmes e criticidade; separe evidência
   observada de hipótese e proponha a próxima verificação.**
2. **Avalie onde a manutenção parece reduzir vibração, mas ainda há risco
   operacional. Cruze efeito da intervenção, indisponibilidade e saúde atual e
   explicite as limitações dos dados.**

## Critérios de sucesso

- usa Metric Views para agregações de negócio;
- não afirma causalidade a partir de correlação;
- informa filtros e período;
- números batem com SQL de referência;
- responde em português e limita rankings;
- reconhece quando uma fonte não permite responder.

## Contingência

Se Genie Agent ou pesquisa aprofundada não estiver disponível, execute as
consultas de referência e use uma captura do ensaio. Declare a limitação; não
apresente chat comum como se fosse pesquisa aprofundada.
