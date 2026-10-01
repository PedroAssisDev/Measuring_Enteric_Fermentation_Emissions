"""Integration tests against the committed reasoned OWL (rdflib only)."""

import pytest

from carbonseco_livestock.config import get_project_paths
from carbonseco_livestock.ontology import build_monthly_emissions_dataframe, load_rdf_graph


@pytest.fixture(scope="module")
def monthly_df():
    paths = get_project_paths()
    if not paths.ontology_reasoned.exists():
        pytest.skip("Reasoned ontology asset not available")
    return build_monthly_emissions_dataframe()


def test_load_rdf_graph() -> None:
    graph = load_rdf_graph()
    assert len(graph) > 0


def test_monthly_dataframe_has_expected_shape(monthly_df) -> None:
    assert not monthly_df.empty
    assert "Reference Scenario Emissions Tier 1" in monthly_df.columns
    assert "Reference Scenario Emissions Tier 2" in monthly_df.columns
    # Feasibility study: no June measurements → at most 11 months.
    assert monthly_df["Month"].nunique() <= 12
    assert 6 not in set(monthly_df["Month"].astype(int))


def test_tier_emissions_positive(monthly_df) -> None:
    assert (monthly_df["Reference Scenario Emissions Tier 1"] > 0).all()
    assert (monthly_df["Reference Scenario Emissions Tier 2"] > 0).all()
