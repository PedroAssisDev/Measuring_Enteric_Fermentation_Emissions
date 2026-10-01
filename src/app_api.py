"""Compatibility shim — prefer carbonseco_livestock.api.app."""

from __future__ import annotations

import uvicorn

from carbonseco_livestock.api.app import app, create_app
from carbonseco_livestock.emissions import (
    calculate_enteric_emission_factor_tier1,
    calculate_enteric_emission_factor_tier2,
    calculate_reference_scenario_emissions,
)

__all__ = [
    "app",
    "create_app",
    "calculate_reference_scenario_emissions",
    "calculate_enteric_emission_factor_tier1",
    "calculate_enteric_emission_factor_tier2",
]


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
