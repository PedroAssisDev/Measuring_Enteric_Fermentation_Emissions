"""IPCC/VCS-style enteric emission calculations used by CarbonSECO services.

Formulas preserve the historical Python implementation used in the ICEIS 2024
feasibility study (see paper equations (1)–(4)).
"""

from __future__ import annotations

from carbonseco_livestock.config import load_scientific_params


def calculate_reference_scenario_emissions(
    greenhouse_gas_emissions: float,
    gwp: float,
) -> float:
    """Convert enteric CH4 (kg) to reference-scenario emissions (tCO2e).

    Corresponds to paper equation (1) applied to a group emission factor:
    BE = EF × GWP × 0.001

    Parameters
    ----------
    greenhouse_gas_emissions:
        Enteric methane emission factor for the group (kg CH4).
    gwp:
        Global Warming Potential of methane (kg CO2e / kg CH4).

    Returns
    -------
    float
        Reference scenario emissions in tCO2e.
    """
    return greenhouse_gas_emissions * gwp / 1000


def calculate_enteric_emission_factor_tier1(
    average_emission_factors: float,
    number_of_heads: float,
    days_on_farm: float,
) -> float:
    """Tier 1 enteric emission factor for a cattle group (kg CH4).

    Paper equation (4):
    EF = EF_production × N × Days
    """
    return average_emission_factors * number_of_heads * days_on_farm


def calculate_enteric_emission_factor_tier2(
    average_energy_density: float,
    average_dry_matter_intake: float,
    average_emission_factor_tier2: float,
    number_of_heads: float,
    days_on_farm: float,
    methane_energy_content: float | None = None,
) -> float:
    """Tier 2 enteric emission factor for a cattle group (kg CH4).

    Combines paper equations (2)–(3):
    GEI = DMI × ED
    EF = (GEI × Ym × N × Days) / (100 × EC)

    The historical implementation multiplies by 0.01 (= Ym/100 when Ym is
    supplied as a percentage-like factor) and divides by EC=55.65.
    """
    if methane_energy_content is None:
        methane_energy_content = load_scientific_params().methane_energy_content_mj_per_kg

    enteric_emission_factor = (
        average_energy_density
        * average_dry_matter_intake
        * average_emission_factor_tier2
        * number_of_heads
        * days_on_farm
        * 0.01
    )
    return enteric_emission_factor / methane_energy_content
