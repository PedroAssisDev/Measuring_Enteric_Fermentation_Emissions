"""Train and persist the linear regression emission projection model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from carbonseco_livestock.config import get_project_paths
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)

FEATURE_COLUMNS = [
    "Days",
    "Average_DMI",
    "Energy_density_of_feed",
    "Average_number_of_heads",
]
TARGET_COLUMN = "Global_emission_Ton_CO2e"


def train_linear_regression_model(
    *,
    data_path: str | Path | None = None,
    model_path: str | Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, Any]:
    """Fit LinearRegression on the synthetic dataset and save the model."""
    paths = get_project_paths()
    source = Path(data_path) if data_path is not None else paths.synthetic_csv
    destination = Path(model_path) if model_path is not None else paths.linear_model

    if not source.exists():
        raise FileNotFoundError(f"Synthetic training CSV not found: {source}")

    df = pd.read_csv(source)
    x = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=random_state
    )

    model = LinearRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    metrics = {
        "mse": float(mean_squared_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "model_path": str(destination),
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, destination)
    logger.info(
        "Trained linear model | MSE=%.2f R2=%.2f | saved to %s",
        metrics["mse"],
        metrics["r2"],
        destination,
    )
    return {"model": model, **metrics}
