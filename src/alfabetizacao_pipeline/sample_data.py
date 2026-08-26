"""Gera uma amostra deterministica e explicitamente sintetica para reproducao local."""

from __future__ import annotations

import csv
from pathlib import Path

from .contracts import CONTRACTS, LEVEL_COLUMNS, TARGET_COLUMNS


MUNICIPALITIES = (
    ("1200401", "Rio Branco", "AC", "Acre", "Norte"),
    ("1200203", "Cruzeiro do Sul", "AC", "Acre", "Norte"),
    ("3550308", "Sao Paulo", "SP", "Sao Paulo", "Sudeste"),
    ("3509502", "Campinas", "SP", "Sao Paulo", "Sudeste"),
    ("4106902", "Curitiba", "PR", "Parana", "Sul"),
    ("4113700", "Londrina", "PR", "Parana", "Sul"),
)

RATES_2023 = {
    "1200401": 52.0,
    "1200203": 49.0,
    "3550308": 62.0,
    "3509502": 65.0,
    "4106902": 64.0,
    "4113700": 61.0,
}

LEVELS = {
    2023: (8.0, 10.0, 12.0, 15.0, 16.0, 14.0, 10.0, 8.0, 7.0),
    2024: (5.0, 8.0, 10.0, 12.0, 14.0, 15.0, 13.0, 12.0, 11.0),
}


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _targets(base: float) -> dict[str, float]:
    return {
        f"meta_alfabetizacao_{year}": round(min(base + 4 * (year - 2024), 95.0), 1)
        for year in range(2024, 2031)
    }


def _rate(municipality_id: str, year: int) -> float:
    return RATES_2023[municipality_id] + (5.0 if year == 2024 else 0.0)


def generate_sample_data(destination: str | Path) -> dict[str, int]:
    """Cria seis CSVs no contrato oficial e um diretorio municipal de enriquecimento.

    Os valores sao didaticos e nao devem ser interpretados como estatistica oficial.
    Os identificadores municipais sao reais; escolas e alunos sao ficticios.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    municipio_rows: list[dict[str, object]] = []
    meta_municipio_rows: list[dict[str, object]] = []
    aluno_rows: list[dict[str, object]] = []

    for municipality_index, (mid, _name, uf, _state, _region) in enumerate(MUNICIPALITIES, 1):
        for year in (2023, 2024):
            rate = _rate(mid, year)
            levels = LEVELS[year]
            result = {
                "ano": year,
                "id_municipio": mid,
                "serie": "2 ano",
                "rede": "Publica",
                "taxa_alfabetizacao": rate,
                "media_portugues": round(730 + (rate - 50) * 1.8, 1),
            }
            result.update(dict(zip(LEVEL_COLUMNS, levels)))
            municipio_rows.append(result)

            target_2024 = RATES_2023[mid] + 7.0
            meta = {
                "ano": year,
                "id_municipio": mid,
                "rede": "Publica",
                "taxa_alfabetizacao": rate,
                "nivel_alfabetizacao": 2 if rate < 60 else 3,
                "percentual_participacao": 88.0 + municipality_index,
            }
            meta.update(_targets(target_2024))
            meta_municipio_rows.append(meta)

            for student_index in range(1, 9):
                present = student_index != 8
                proficiency = 670 + student_index * 19 + (year - 2023) * 14 + municipality_index * 2
                alfabetized = present and proficiency >= 743
                aluno_rows.append(
                    {
                        "ano": year,
                        "id_municipio": mid,
                        "id_escola": f"ESC{municipality_index:02d}",
                        "id_aluno": f"A{year}{municipality_index:02d}{student_index:03d}",
                        "caderno": f"C{(student_index % 4) + 1}",
                        "serie": "2 ano",
                        "rede": "Publica",
                        "presenca": "Presente" if present else "Ausente",
                        "preenchimento_caderno": "Preenchido" if present else "Nao preenchido",
                        "alfabetizado": "Sim" if alfabetized else "Nao",
                        "proficiencia": proficiency if present else "",
                        "peso_aluno": 1.0,
                    }
                )

    uf_rows: list[dict[str, object]] = []
    meta_uf_rows: list[dict[str, object]] = []
    for uf in ("AC", "SP", "PR"):
        municipality_ids = [mid for mid, _n, item_uf, _s, _r in MUNICIPALITIES if item_uf == uf]
        base_2023 = sum(RATES_2023[mid] for mid in municipality_ids) / len(municipality_ids)
        for year in (2023, 2024):
            rate = base_2023 + (5.0 if year == 2024 else 0.0)
            result = {
                "ano": year,
                "sigla_uf": uf,
                "serie": "2 ano",
                "rede": "Publica",
                "taxa_alfabetizacao": round(rate, 1),
                "media_portugues": round(730 + (rate - 50) * 1.8, 1),
            }
            result.update(dict(zip(LEVEL_COLUMNS, LEVELS[year])))
            uf_rows.append(result)

            meta = {
                "ano": year,
                "sigla_uf": uf,
                "rede": "Publica",
                "taxa_alfabetizacao": round(rate, 1),
                "percentual_participacao": 92.0,
            }
            meta.update(_targets(base_2023 + 7.0))
            meta_uf_rows.append(meta)

    national_2023 = sum(RATES_2023.values()) / len(RATES_2023)
    brasil_rows: list[dict[str, object]] = []
    for year in (2023, 2024):
        rate = national_2023 + (5.0 if year == 2024 else 0.0)
        row = {
            "ano": year,
            "rede": "Publica",
            "taxa_alfabetizacao": round(rate, 1),
            "percentual_participacao": 91.0,
        }
        row.update(_targets(national_2023 + 7.0))
        brasil_rows.append(row)

    tables = {
        "uf": uf_rows,
        "meta_alfabetizacao_brasil": brasil_rows,
        "meta_alfabetizacao_uf": meta_uf_rows,
        "meta_alfabetizacao_municipio": meta_municipio_rows,
        "municipio": municipio_rows,
        "alunos": aluno_rows,
    }
    for table_name, rows in tables.items():
        _write_csv(destination / f"{table_name}.csv", CONTRACTS[table_name].fields, rows)

    reference_fields = ("id_municipio", "nome_municipio", "sigla_uf", "nome_uf", "regiao")
    reference_rows = [
        dict(zip(reference_fields, (mid, name, uf, state, region)))
        for mid, name, uf, state, region in MUNICIPALITIES
    ]
    _write_csv(destination / "municipios_referencia.csv", reference_fields, reference_rows)
    return {name: len(rows) for name, rows in tables.items()}

