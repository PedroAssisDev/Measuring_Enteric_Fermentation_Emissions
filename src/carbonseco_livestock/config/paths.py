"""Portable project path resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Locate repository root by walking up until pyproject.toml is found."""
    env_root = os.environ.get("CARBONSECO_ROOT")
    if env_root:
        return Path(env_root).resolve()

    current = (start or Path(__file__)).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    # Fallback: src/carbonseco_livestock/config -> repo root (4 levels up)
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class ProjectPaths:
    """Canonical locations for data, models, ontology assets, and results."""

    root: Path

    @property
    def configs(self) -> Path:
        return self.root / "configs"

    @property
    def scientific_params(self) -> Path:
        return self.configs / "scientific_params.yaml"

    @property
    def data_raw(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def data_processed(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def raw_farm_csv(self) -> Path:
        return self.data_raw / "pesoXleite.csv"

    @property
    def processed_farm_csv(self) -> Path:
        return self.data_processed / "pesoXleite_parsed.csv"

    @property
    def synthetic_csv(self) -> Path:
        return self.data_processed / "sintetico.csv"

    @property
    def models(self) -> Path:
        return self.root / "models"

    @property
    def linear_model(self) -> Path:
        return self.models / "linear_regression_model.pkl"

    @property
    def ontology_assets(self) -> Path:
        return self.root / "ontology_assets"

    @property
    def ontology_tbox(self) -> Path:
        return self.ontology_assets / "ontologia.owl"

    @property
    def ontology_populated(self) -> Path:
        return self.ontology_assets / "ontologia_final_populada.owl"

    @property
    def ontology_reasoned(self) -> Path:
        return self.ontology_assets / "ontologia_populada_sync_reasoner_pellet.owl"

    @property
    def results(self) -> Path:
        return self.root / "results"


def get_project_paths(start: Path | None = None) -> ProjectPaths:
    return ProjectPaths(root=find_project_root(start))
