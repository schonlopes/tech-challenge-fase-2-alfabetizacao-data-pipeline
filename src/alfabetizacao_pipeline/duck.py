"""Utilitarios DuckDB compartilhados pelas etapas locais."""

from __future__ import annotations

from pathlib import Path

import duckdb


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("SET preserve_insertion_order = false")
    con.execute("SET threads = 4")
    return con


def sql_path(path: str | Path) -> str:
    return str(Path(path).resolve()).replace("\\", "/").replace("'", "''")


def parquet_glob(path: str | Path) -> str:
    return f"{sql_path(path)}/**/*.parquet"


def copy_partitioned(
    con: duckdb.DuckDBPyConnection,
    query: str,
    destination: str | Path,
    partition_columns: tuple[str, ...] = ("ano",),
) -> None:
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    partitions = ", ".join(partition_columns)
    con.execute(
        f"""
        COPY ({query}) TO '{sql_path(dest)}'
        (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY ({partitions}),
         OVERWRITE_OR_IGNORE TRUE, ROW_GROUP_SIZE 100000)
        """
    )


def copy_single(
    con: duckdb.DuckDBPyConnection,
    query: str,
    destination: str | Path,
) -> None:
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"COPY ({query}) TO '{sql_path(dest)}' "
        "(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)"
    )

