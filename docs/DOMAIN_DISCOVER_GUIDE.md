# Domain, Subdomain, Page e Discover

> Interface em evolução: Domains e Discover estavam em Public Preview e Pages
> em Beta em 01/10/2026. Os rótulos podem variar por cloud/região.

## Parte A — antes dos consumidores

1. Abra **Discover** e acesse a área de **Domains**.
2. Selecione **Create domain**.
3. Use o conteúdo de `config/domain_page_content.md` para criar
   **Operações Industriais**.
4. Defina o grupo responsável indicado pelo instrutor; não use uma pessoa como
   proprietário único da demonstração.
5. Crie o Subdomain **Saúde de Ativos**.
6. Adicione ao Subdomain:
   - `gold_asset_health_current`;
   - `gold_asset_health_hourly`;
   - `gold_site_operations_daily`;
   - `gold_maintenance_impact`;
   - `mv_operational_health`;
   - `mv_maintenance_reliability`.
7. Revise descrições e mantenha o Domain em **Draft**.

**Verificação:** os seis ativos aparecem no Subdomain e abrem no Catalog
Explorer sem erro de permissão.

## Parte B — depois do Agent, Dashboard e App

1. No Subdomain, selecione **Create page** ou a ação equivalente.
2. Crie **Central de Saúde Operacional**.
3. Adicione resumo e seções do arquivo de configuração.
4. Insira links/cartões para:
   - os dois Metric Views;
   - o Genie Agent;
   - o AI/BI Dashboard;
   - a Databricks App.
5. Abra a prévia como consumidor.
6. Verifique permissões de cada ativo; uma Page não amplia acesso.
7. Publique a Page e, depois, o Domain.
8. Volte ao Discover, pesquise “saúde de ativos” e abra o resultado.

**Critério de sucesso:** um consumidor autorizado encontra a Page por busca e
chega ao Agent, Dashboard e App sem receber permissão adicional indevida.

## Contingência

Se criação/publicação estiver indisponível, o instrutor demonstra a versão de
ensaio. O participante registra a estrutura no arquivo de conteúdo e continua
usando os links diretos dos ativos.
