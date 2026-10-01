"""Farm milking CSV preprocessing for EntericMeasureOnto population.

Aggregates three daily milkings (sum milk, mean weight) and, when diet
measurements are unavailable, attaches energy density / DMI placeholders
used in the feasibility study Tier-2 enrichment step.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from carbonseco_livestock.config import get_project_paths, load_scientific_params
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)


def parse_to_float(value: object) -> float | None:
    """Convert a cell to float; return None if conversion fails."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        logger.warning("Could not convert value %r to float", value)
        return None


def parse_date(month: object, year: int = 2021) -> pd.Timestamp:
    """Map a month number to the last day of that month in the study year."""
    date = pd.to_datetime(f"{year}-{int(month)}-01") + pd.offsets.MonthEnd(0)
    return date


def parse_farm_file(
    file_path: str | Path | None = None,
    *,
    output_path: str | Path | None = None,
    random_seed: int | None = None,
    write_output: bool = True,
) -> pd.DataFrame:
    """Parse raw farm CSV into the processed schema used by ontology population.

    Parameters
    ----------
    file_path:
        Raw CSV with columns Brinco, Peso, Leite, Date (month number).
    output_path:
        Destination for the processed CSV. Defaults to data/processed/.
    random_seed:
        Optional seed for ED/DMI noise. Leave None to preserve historical
        unseeded behavior when regenerating; prefer not regenerating the
        committed processed file in scientific workflows.
    write_output:
        When True, persist the processed DataFrame.
    """
    paths = get_project_paths()
    params = load_scientific_params()
    source = Path(file_path) if file_path is not None else paths.raw_farm_csv
    destination = Path(output_path) if output_path is not None else paths.processed_farm_csv

    if not source.exists():
        raise FileNotFoundError(f"Farm CSV not found: {source}")

    df = pd.read_csv(source)
    df["Brinco"] = df["Brinco"].astype(str)
    df["Peso"] = df["Peso"].apply(parse_to_float)
    df["Leite"] = df["Leite"].apply(parse_to_float)
    df["Date"] = df["Date"].apply(parse_date)

    result_df = (
        df.groupby(["Date", "Brinco"], as_index=False)
        .agg({"Leite": "sum", "Peso": "mean"})
    )
    result_df["Leite"] = result_df["Leite"].round(2)
    result_df["Peso"] = result_df["Peso"].round(2)

    rng = np.random.default_rng(random_seed)
    ed_base = params.default_energy_density_mj_per_kg
    dmi_base = params.default_dry_matter_intake_kg_per_head_per_day
    ed_noise = params.energy_density_noise_half_range
    dmi_noise = params.dry_matter_intake_noise_half_range
    n = len(result_df)

    # Historical implementation used np.random.uniform without a seed.
    # When random_seed is None we keep that unseeded NumPy global API.
    if random_seed is None:
        result_df["energyDensity"] = np.round(
            ed_base + np.random.uniform(-ed_noise, ed_noise, size=n), 2
        )
        result_df["dryMatterIntake"] = np.round(
            dmi_base + np.random.uniform(-dmi_noise, dmi_noise, size=n), 2
        )
    else:
        result_df["energyDensity"] = np.round(
            ed_base + rng.uniform(-ed_noise, ed_noise, size=n), 2
        )
        result_df["dryMatterIntake"] = np.round(
            dmi_base + rng.uniform(-dmi_noise, dmi_noise, size=n), 2
        )

    if write_output:
        destination.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(destination, index=False)
        logger.info("Wrote processed farm data to %s", destination)

    return result_df
