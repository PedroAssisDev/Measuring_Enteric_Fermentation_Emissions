"""Load and expose scientific parameters from YAML configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from carbonseco_livestock.config.paths import get_project_paths


@dataclass(frozen=True)
class ScientificParams:
    """Scientific constants used by ontology population and emission formulas."""

    gwp_methane: float
    emission_factor_tier1_kg_ch4_per_head_per_day: float
    emission_factor_tier2_ym_percent: float
    methane_energy_content_mj_per_kg: float
    days_per_month_approximation: int
    default_energy_density_mj_per_kg: float
    default_dry_matter_intake_kg_per_head_per_day: float
    energy_density_noise_half_range: float
    dry_matter_intake_noise_half_range: float
    synthetic_training_gwp_factor: float
    paper_projection_days: float
    paper_projection_average_dmi: float
    paper_projection_energy_density: float
    paper_projection_heads: float
    paper_projection_expected_tco2e: float

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> ScientificParams:
        projection = data.get("paper_projection", {})
        return cls(
            gwp_methane=float(data["gwp_methane"]),
            emission_factor_tier1_kg_ch4_per_head_per_day=float(
                data["emission_factor_tier1_kg_ch4_per_head_per_day"]
            ),
            emission_factor_tier2_ym_percent=float(data["emission_factor_tier2_ym_percent"]),
            methane_energy_content_mj_per_kg=float(data["methane_energy_content_mj_per_kg"]),
            days_per_month_approximation=int(data["days_per_month_approximation"]),
            default_energy_density_mj_per_kg=float(data["default_energy_density_mj_per_kg"]),
            default_dry_matter_intake_kg_per_head_per_day=float(
                data["default_dry_matter_intake_kg_per_head_per_day"]
            ),
            energy_density_noise_half_range=float(data["energy_density_noise_half_range"]),
            dry_matter_intake_noise_half_range=float(data["dry_matter_intake_noise_half_range"]),
            synthetic_training_gwp_factor=float(data["synthetic_training_gwp_factor"]),
            paper_projection_days=float(projection["days"]),
            paper_projection_average_dmi=float(projection["average_dmi"]),
            paper_projection_energy_density=float(projection["energy_density_of_feed"]),
            paper_projection_heads=float(projection["average_number_of_heads"]),
            paper_projection_expected_tco2e=float(projection["expected_tco2e"]),
        )


def load_scientific_params(path: Path | None = None) -> ScientificParams:
    params_path = path or get_project_paths().scientific_params
    with params_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return ScientificParams.from_mapping(raw)
