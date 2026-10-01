# Fábrica de dados

Utilitário de manutenção, fora da agenda do workshop. Os participantes usam os
seis arquivos Parquet já versionados em `data/prepared/`.

Para reproduzir os dados:

```bash
uv run --with polars --with numpy --with pyarrow \
  python tools/data_factory/generate_data.py --output data/prepared
```

A geração é determinística (`seed=42`), não usa fontes externas e não contém
nomes de pessoas, contatos, identificadores reais ou dados de uma empresa.
