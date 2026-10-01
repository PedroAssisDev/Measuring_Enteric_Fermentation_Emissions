"""Unit tests for IPCC/VCS-style emission calculators (historical formulas)."""

from carbonseco_livestock.emissions import (
    calculate_enteric_emission_factor_tier1,
    calculate_enteric_emission_factor_tier2,
    calculate_reference_scenario_emissions,
)


def test_tier1_emission_factor() -> None:
    # EF = 78 * 100 heads * 30 days
    result = calculate_enteric_emission_factor_tier1(78.0, 100, 30)
    assert result == 78.0 * 100 * 30


def test_reference_scenario_emissions() -> None:
    # BE = EF * GWP / 1000
    result = calculate_reference_scenario_emissions(234000.0, 28.0)
    assert result == 234000.0 * 28.0 / 1000


def test_tier2_emission_factor_matches_historical_formula() -> None:
    ed, dmi, ym, heads, days = 18.0, 25.0, 6.5, 100.0, 31.0
    expected = (ed * dmi * ym * heads * days * 0.01) / 55.65
    result = calculate_enteric_emission_factor_tier2(ed, dmi, ym, heads, days)
    assert result == expected
