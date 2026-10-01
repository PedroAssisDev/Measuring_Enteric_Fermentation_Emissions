#!/usr/bin/env python
"""Reproduce the ICEIS 2024 feasibility-study ML projection (598.48 tCO2e)."""

from carbonseco_livestock.config import load_scientific_params
from carbonseco_livestock.ml import predict_emissions


def main() -> None:
    params = load_scientific_params()
    prediction = predict_emissions(
        params.paper_projection_days,
        params.paper_projection_average_dmi,
        params.paper_projection_energy_density,
        params.paper_projection_heads,
    )
    print("Feasibility-study projection inputs:")
    print(f"  days={params.paper_projection_days}")
    print(f"  average_dmi={params.paper_projection_average_dmi}")
    print(f"  energy_density={params.paper_projection_energy_density}")
    print(f"  heads={params.paper_projection_heads}")
    print(f"Predicted tCO2e: {prediction:.8f}")
    print(f"Rounded (paper): {round(prediction, 2)}")
    print(f"Expected (paper): {params.paper_projection_expected_tco2e}")


if __name__ == "__main__":
    main()
