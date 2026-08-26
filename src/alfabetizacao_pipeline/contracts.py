"""Contratos das tabelas oficiais da Base dos Dados.

Os nomes e tipos foram conferidos na pagina oficial do conjunto
``br_inep_avaliacao_alfabetizacao`` em 2026-08-26.
"""

from __future__ import annotations

from dataclasses import dataclass


LEVEL_COLUMNS = tuple(f"proporcao_aluno_nivel_{i}" for i in range(9))
TARGET_COLUMNS = tuple(f"meta_alfabetizacao_{year}" for year in range(2024, 2031))


@dataclass(frozen=True)
class TableContract:
    name: str
    fields: tuple[str, ...]
    key: tuple[str, ...]
    description: str


CONTRACTS: dict[str, TableContract] = {
    "uf": TableContract(
        name="uf",
        fields=(
            "ano", "sigla_uf", "serie", "rede", "taxa_alfabetizacao",
            "media_portugues", *LEVEL_COLUMNS,
        ),
        key=("ano", "sigla_uf", "serie", "rede"),
        description="Resultados agregados da avaliacao por UF, serie e rede.",
    ),
    "meta_alfabetizacao_brasil": TableContract(
        name="meta_alfabetizacao_brasil",
        fields=(
            "ano", "rede", "taxa_alfabetizacao", *TARGET_COLUMNS,
            "percentual_participacao",
        ),
        key=("ano", "rede"),
        description="Resultado nacional e metas anuais de 2024 a 2030.",
    ),
    "meta_alfabetizacao_uf": TableContract(
        name="meta_alfabetizacao_uf",
        fields=(
            "ano", "sigla_uf", "rede", "taxa_alfabetizacao", *TARGET_COLUMNS,
            "percentual_participacao",
        ),
        key=("ano", "sigla_uf", "rede"),
        description="Resultado e metas anuais por UF.",
    ),
    "meta_alfabetizacao_municipio": TableContract(
        name="meta_alfabetizacao_municipio",
        fields=(
            "ano", "id_municipio", "rede", "taxa_alfabetizacao", *TARGET_COLUMNS,
            "nivel_alfabetizacao", "percentual_participacao",
        ),
        key=("ano", "id_municipio", "rede"),
        description="Resultado, nivel e metas anuais por municipio.",
    ),
    "municipio": TableContract(
        name="municipio",
        fields=(
            "ano", "id_municipio", "serie", "rede", "taxa_alfabetizacao",
            "media_portugues", *LEVEL_COLUMNS,
        ),
        key=("ano", "id_municipio", "serie", "rede"),
        description="Resultados agregados da avaliacao por municipio, serie e rede.",
    ),
    "alunos": TableContract(
        name="alunos",
        fields=(
            "ano", "id_municipio", "id_escola", "id_aluno", "caderno", "serie",
            "rede", "presenca", "preenchimento_caderno", "alfabetizado",
            "proficiencia", "peso_aluno",
        ),
        key=("ano", "id_aluno"),
        description="Microdados pseudonimizados de alunos avaliados.",
    ),
}

OFFICIAL_DATASET = "basedosdados.br_inep_avaliacao_alfabetizacao"
LITERACY_CUTOFF = 743.0

