"""Load the persisted linear model and produce emission projections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from carbonseco_livestock.config import get_project_paths
from carbonseco_livestock.ml.train import FEATURE_COLUMNS


def load_emission_model(model_path: str | Path | None = None) -> Any:
    paths = get_project_paths()
    target = Path(model_path) if model_path is not None else paths.linear_model
    if not target.exists():
        raise FileNotFoundError(f"Trained model not found: {target}")
    return joblib.load(target)


def predict_emissions(
    days: float,
    average_dmi: float,
    energy_density_of_feed: float,
    average_number_of_heads: float,
    *,
    model: Any | None = None,
    model_path: str | Path | None = None,
) -> float:
    """Predict projected total emissions (tCO2e) for the given scenario inputs."""
    estimator = model if model is not None else load_emission_model(model_path)
    frame = pd.DataFrame(
        {
            "Days": [days],
            "Average_DMI": [average_dmi],
            "Energy_density_of_feed": [energy_density_of_feed],
            "Average_number_of_heads": [average_number_of_heads],
        }
    )[FEATURE_COLUMNS]
    prediction = estimator.predict(frame)
    return float(prediction[0])
