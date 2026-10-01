"""SPARQL queries and monthly emission dataframe construction."""

from __future__ import annotations

from calendar import monthrange
from pathlib import Path

import pandas as pd
from rdflib import Graph, Namespace

from carbonseco_livestock.config import get_project_paths
from carbonseco_livestock.domain import OntologyIRI
from carbonseco_livestock.emissions import (
    calculate_enteric_emission_factor_tier1,
    calculate_enteric_emission_factor_tier2,
    calculate_reference_scenario_emissions,
)

OWL = Namespace(OntologyIRI.BASE)
RDF = Namespace(OntologyIRI.RDF)

QUERY_GWP_EMISSION_FACTOR = """
SELECT ?cattle ?gwp ?emissionFactorTier1
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:gwp ?gwp .
  ?cattle owl:emissionFactorTier1 ?emissionFactorTier1 .
}
"""

QUERY_MONTHLY_AGGREGATES = """
SELECT ?month ?year (COUNT(DISTINCT ?cattle) AS ?countDairyCattle) (SUM(?milkProduction) AS ?totalMilk)
                    (AVG(?weight) AS ?averageWeight)  (AVG(?energyDensity) AS ?averageEnergyDensity)
                    (AVG(?dryMatterIntake) AS ?averageDryMatterIntake)
                    (AVG(?emissionFactorTier2) AS ?averageEmissionFactorTier2)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:measurementDate ?date .
  ?measurementData owl:milkProduction ?milkProduction .
  ?measurementData owl:weight ?weight .
  ?measurementData owl:energyDensity ?energyDensity .
  ?measurementData owl:dryMatterIntake ?dryMatterIntake .
  ?measurementData owl:emissionFactorTier2 ?emissionFactorTier2 .
  BIND(MONTH(?date) AS ?month)
  BIND(YEAR(?date) AS ?year)
}
GROUP BY ?month ?year
ORDER BY ?year ?month
"""

SPARQL_TIER1_SUM = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?individualEntericEmissionTier1) AS ?totalSum)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:individualEntericEmissionTier1 ?individualEntericEmissionTier1 .
}
"""

SPARQL_TIER2_SUM = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?individualEntericEmissionTier2) AS ?totalSum)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:individualEntericEmissionTier2 ?individualEntericEmissionTier2 .
}
"""

SPARQL_MILK_SUM = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?milkProduction) AS ?totalMilk)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:milkProduction ?milkProduction .
}
"""


def load_rdf_graph(ontology_path: str | Path | None = None) -> Graph:
    """Load the reasoned (or provided) OWL file into an rdflib Graph."""
    paths = get_project_paths()
    target = Path(ontology_path) if ontology_path is not None else paths.ontology_reasoned
    if not target.exists():
        raise FileNotFoundError(f"Ontology OWL not found: {target}")
    graph = Graph()
    graph.parse(str(target), format="xml")
    return graph


def _average_gwp_and_tier1(graph: Graph) -> tuple[float, float]:
    rows = list(graph.query(QUERY_GWP_EMISSION_FACTOR, initNs={"rdf": RDF, "owl": OWL}))
    if not rows:
        raise ValueError("No DairyCattle GWP/emissionFactorTier1 values found in ontology")
    gwp_values = [float(row.gwp) for row in rows]
    ef1_values = [float(row.emissionFactorTier1) for row in rows]
    return sum(gwp_values) / len(gwp_values), sum(ef1_values) / len(ef1_values)


def build_monthly_emissions_dataframe(
    graph: Graph | None = None,
    *,
    ontology_path: str | Path | None = None,
    include_diet_columns: bool = False,
) -> pd.DataFrame:
    """Build the monthly emissions table used by API and dashboard.

    Tier 1/2 group calculations are performed in Python (same as the original
    services), using ontology measurement aggregates per month.
    """
    graph = graph if graph is not None else load_rdf_graph(ontology_path)
    gwp, emission_factor_tier1 = _average_gwp_and_tier1(graph)

    columns = [
        "Month",
        "Year",
        "Count Dairy Cattle",
        "Total Milk",
        "Average Weight",
        "Number of days",
        "Enteric Emission Factor Tier 1",
        "Reference Scenario Emissions Tier 1",
        "Enteric Emission Factor Tier 2",
        "Reference Scenario Emissions Tier 2",
    ]
    if include_diet_columns:
        columns = [
            "Month",
            "Year",
            "Count Dairy Cattle",
            "Total Milk",
            "Average Weight",
            "Number of days",
            "gwp",
            "emissionFactorTier1",
            "averageEnergyDensity",
            "averageDryMatterIntake",
            "averageEmissionFactorTier2",
            "Enteric Emission Factor Tier 1",
            "Reference Scenario Emissions Tier 1",
            "Enteric Emission Factor Tier 2",
            "Reference Scenario Emissions Tier 2",
        ]

    data: list[list[object]] = []
    for row in graph.query(QUERY_MONTHLY_AGGREGATES, initNs={"rdf": RDF, "owl": OWL}):
        year = int(row.year)
        month = int(row.month)
        days = int(monthrange(year, month)[1])
        count_dairy_cattle = int(row.countDairyCattle)
        total_milk = float(row.totalMilk) * days
        average_weight = float(row.averageWeight)
        average_energy_density = float(row.averageEnergyDensity)
        average_dry_matter_intake = float(row.averageDryMatterIntake)
        average_emission_factor_tier2 = float(row.averageEmissionFactorTier2)

        enteric_ef_tier1 = calculate_enteric_emission_factor_tier1(
            emission_factor_tier1, count_dairy_cattle, days
        )
        reference_tier1 = calculate_reference_scenario_emissions(enteric_ef_tier1, gwp)
        enteric_ef_tier2 = calculate_enteric_emission_factor_tier2(
            average_energy_density,
            average_dry_matter_intake,
            average_emission_factor_tier2,
            count_dairy_cattle,
            days,
        )
        reference_tier2 = calculate_reference_scenario_emissions(enteric_ef_tier2, gwp)

        if include_diet_columns:
            data.append(
                [
                    month,
                    year,
                    count_dairy_cattle,
                    total_milk,
                    average_weight,
                    days,
                    gwp,
                    emission_factor_tier1,
                    average_energy_density,
                    average_dry_matter_intake,
                    average_emission_factor_tier2,
                    enteric_ef_tier1,
                    reference_tier1,
                    enteric_ef_tier2,
                    reference_tier2,
                ]
            )
        else:
            data.append(
                [
                    month,
                    year,
                    count_dairy_cattle,
                    total_milk,
                    average_weight,
                    days,
                    enteric_ef_tier1,
                    reference_tier1,
                    enteric_ef_tier2,
                    reference_tier2,
                ]
            )

    return pd.DataFrame(data, columns=columns)
