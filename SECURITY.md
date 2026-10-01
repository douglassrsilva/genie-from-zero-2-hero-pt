# Segurança e privacidade

- Os dados são integralmente sintéticos e não contêm PII.
- Não há nomes, contatos, identificadores de clientes ou empresas reais.
- Catálogo, schema, Warehouse e workspace são fornecidos em tempo de execução.
- O código não inclui token, senha, host, perfil local ou arquivo de autenticação.
- A App usa a identidade de serviço do Databricks Apps e privilégios mínimos.
- O modo local da App lê somente os Parquet sintéticos e não exige credenciais.

Antes de publicar, execute:

```bash
rg -n -i '(token|password|secret|client[_-]?secret|api[_-]?key)\s*[:=]' .
rg -n 'https://[^ ]*cloud\.databricks\.com|[0-9a-f]{16}' .
```

Resultados em documentação que descrevem os termos de segurança devem ser
revisados pelo contexto; valores reais nunca devem aparecer.

Para relatar uma vulnerabilidade, use um canal privado do mantenedor. Não abra
uma issue pública contendo credenciais ou dados do ambiente.
