# Genie One e Genie Ontology

## Genie One

Genie One é o nome atual da experiência anteriormente chamada Databricks One.
Ela deve ser habilitada e testada pelo administrador antes do workshop.

Roteiro do consumidor:

1. entre na experiência Genie One com um usuário não administrador;
2. localize **Central de Saúde Operacional** no Discover;
3. abra o Genie Agent e pergunte “quais regiões concentram mais ativos
   críticos?”;
4. abra o Dashboard a partir da Page e compare o total;
5. abra a App e filtre a região líder;
6. confirme que um ativo sem permissão continua inacessível.

Se Genie One não estiver disponível, faça os mesmos passos no Discover padrão
e declare a contingência.

## Genie Ontology

Genie Ontology estava em Public Preview em 01/10/2026. Ela não é um objeto
criado separadamente por botão, DDL ou API. Neste workshop, ela emerge de:

| Contexto | Evidência criada |
|---|---|
| Explícito | dimensões, medidas e sinônimos dos Metric Views |
| Explícito | Domain, Subdomain e Page |
| Explícito | comentários, descrições e instruções do Agent |
| Inferido | consultas do Dashboard e perguntas validadas do Agent |
| Aplicado | navegação e respostas no Genie One |

Demonstração:

1. peça ao Agent: **O que significa um ativo crítico neste domínio?**;
2. confirme que a resposta usa o limite `health_score < 60` das instruções;
3. peça: **Relacione a condição atual com o impacto de manutenção e separe fato
   de hipótese.**;
4. identifique quais relações vêm da semântica explícita e quais foram
   inferidas pelo uso.

Critério de sucesso: a turma consegue apontar ao menos três ativos de contexto
que formam a Ontology e entende que não há um artefato extra a criar.
