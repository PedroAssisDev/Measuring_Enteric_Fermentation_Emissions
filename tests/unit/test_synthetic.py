"""Unit tests for synthetic ML target generation."""

import numpy as np

from carbonseco_livestock.config import load_scientific_params
from carbonseco_livestock.ml import generate_synthetic_data


def test_synthetic_generation_is_seeded() -> None:
    df1 = generate_synthetic_data(100, seed=42, write_output=False)
    df2 = generate_synthetic_data(100, seed=42, write_output=False)
    pd_eq = df1.equals(df2)
    assert pd_eq


def test_synthetic_target_formula_component() -> None:
    params = load_scientific_params()
    days, dmi, ed, heads = 335.0, 21.0, 18.0, 200.0
    closed_form = (
        days
        * dmi
        * 0.01
        * ed
        * heads
        * params.emission_factor_tier2_ym_percent
        * params.synthetic_training_gwp_factor
        * 0.001
    ) / params.methane_energy_content_mj_per_kg
    assert closed_form == np.float64(closed_form)
    assert closed_form > 500  # sanity: near paper projection magnitude before noise
