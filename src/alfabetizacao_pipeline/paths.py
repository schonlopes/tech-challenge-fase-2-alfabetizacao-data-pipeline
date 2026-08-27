"""Caminhos do projeto e protecoes para escrita nas camadas do lake."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @classmethod
    def from_root(cls, root: str | Path | None = None) -> "ProjectPaths":
        if root is None:
            root = Path(__file__).resolve().parents[2]
        return cls(Path(root).resolve())

    @property
    def sample(self) -> Path:
        return self.root / "data" / "sample"

    @property
    def lake(self) -> Path:
        return self.root / "data" / "lake"

    @property
    def bronze(self) -> Path:
        return self.lake / "bronze"

    @property
    def bronze_stream(self) -> Path:
        return self.lake / "bronze_stream"

    @property
    def silver(self) -> Path:
        return self.lake / "silver"

    @property
    def gold(self) -> Path:
        return self.lake / "gold"

    @property
    def stream_inbox(self) -> Path:
        return self.root / "data" / "stream" / "inbox" / "alunos.jsonl"

    @property
    def stream_checkpoint(self) -> Path:
        return self.root / "data" / "stream" / "checkpoints" / "alunos.offset"

    @property
    def stream_dlq(self) -> Path:
        return self.root / "data" / "stream" / "dlq" / "alunos_invalidos.jsonl"

    @property
    def staging(self) -> Path:
        return self.root / "data" / "staging"

    @property
    def evidence(self) -> Path:
        return self.root / "artifacts" / "evidence"

    def ensure(self) -> None:
        for path in (
            self.sample,
            self.bronze,
            self.bronze_stream,
            self.silver,
            self.gold,
            self.stream_inbox.parent,
            self.stream_checkpoint.parent,
            self.stream_dlq.parent,
            self.staging,
            self.evidence,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def replace_derived_layer(self, layer: str) -> Path:
        """Remove somente Silver ou Gold, sempre abaixo do lake configurado."""
        if layer not in {"silver", "gold"}:
            raise ValueError("Somente as camadas derivadas silver/gold podem ser substituidas.")
        target = (self.lake / layer).resolve()
        lake = self.lake.resolve()
        if target.parent != lake or target.name != layer:
            raise ValueError(f"Destino inseguro para substituicao: {target}")
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        return target
