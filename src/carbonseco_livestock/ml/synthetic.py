"""Synthetic dataset generation for the linear-regression projection module."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from carbonseco_livestock.config import get_project_paths, load_scientific_params
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)


def generate_synthetic_data(
    num_samples: int = 50_000,
    *,
    seed: int = 42,
    output_path: str | Path | None = None,
    write_output: bool = True,
) -> pd.DataFrame:
    """Generate synthetic farm-period samples labeled with a Tier-2-like target."""
    params = load_scientific_params()
    np.random.seed(seed)

    days = np.random.randint(30, 365, size=num_samples)
    avg_dmi = np.random.uniform(14, 27, size=num_samples)
    energy_density = np.random.uniform(14, 27, size=num_samples)
    avg_heads = np.random.uniform(50, 400, size=num_samples)

    target_variable = (
        days
        * avg_dmi
        * 0.01
        * energy_density
        * avg_heads
        * params.emission_factor_tier2_ym_percent
        * params.synthetic_training_gwp_factor
        * 0.001
    ) / params.methane_energy_content_mj_per_kg

    noise = np.random.normal(-50, 50, size=num_samples)
    target_variable = target_variable + noise

    frame = pd.DataFrame(
        {
            "Days": days,
            "Average_DMI": avg_dmi,
            "Energy_density_of_feed": energy_density,
            "Average_number_of_heads": avg_heads,
            "Global_emission_Ton_CO2e": target_variable,
        }
    )

    if write_output:
        paths = get_project_paths()
        destination = Path(output_path) if output_path is not None else paths.synthetic_csv
        destination.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(destination, index=False)
        logger.info("Wrote synthetic dataset (%s rows) to %s", num_samples, destination)

    return frame
