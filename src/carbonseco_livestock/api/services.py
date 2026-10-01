"""Shared service helpers for FastAPI endpoints."""

from __future__ import annotations

from typing import Any

import owlready2 as olwr
import pandas as pd

from carbonseco_livestock.config import load_scientific_params
from carbonseco_livestock.ml import load_emission_model, predict_emissions
from carbonseco_livestock.ontology.queries import (
    SPARQL_MILK_SUM,
    SPARQL_TIER1_SUM,
    SPARQL_TIER2_SUM,
    build_monthly_emissions_dataframe,
    load_rdf_graph,
)
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)


class EmissionServices:
    """Lazy-loaded ontology graph, monthly frame, and ML model."""

    def __init__(self) -> None:
        self._graph = None
        self._monthly_df: pd.DataFrame | None = None
        self._grouped_df: pd.DataFrame | None = None
        self._model = None
        self._onto = None

    def load(self, *, sync_pellet: bool = True) -> None:
        from carbonseco_livestock.config import get_project_paths

        paths = get_project_paths()
        self._model = load_emission_model()
        self._onto = olwr.get_ontology(str(paths.ontology_reasoned)).load()
        if sync_pellet:
            try:
                olwr.sync_reasoner_pellet(
                    infer_data_property_values=True,
                    infer_property_values=True,
                )
            except Exception as exc:
                logger.warning("Pellet sync skipped/failed at API startup: %s", exc)
        self._graph = load_rdf_graph()
        self._monthly_df = build_monthly_emissions_dataframe(self._graph)
        self._grouped_df = (
            self._monthly_df.groupby(["Year", "Month"], as_index=False)
            .agg(
                {
                    "Count Dairy Cattle": "sum",
                    "Number of days": "mean",
                    "Total Milk": "sum",
                    "Enteric Emission Factor Tier 1": "sum",
                    "Reference Scenario Emissions Tier 1": "sum",
                    "Enteric Emission Factor Tier 2": "sum",
                    "Reference Scenario Emissions Tier 2": "sum",
                }
            )
            .sort_values(["Year", "Month"])
        )

    @property
    def model(self) -> Any:
        if self._model is None:
            self.load()
        return self._model

    @property
    def grouped_df(self) -> pd.DataFrame:
        if self._grouped_df is None:
            self.load()
        assert self._grouped_df is not None
        return self._grouped_df

    def predict(
        self,
        days: float,
        average_dmi: float,
        energy_density_of_feed: float,
        average_number_of_heads: float,
    ) -> list[float]:
        value = predict_emissions(
            days,
            average_dmi,
            energy_density_of_feed,
            average_number_of_heads,
            model=self.model,
        )
        return [value]

    def total_year_aggregates(self) -> dict[str, list[float]]:
        params = load_scientific_params()
        gwp = params.gwp_methane

        def _scale(query: str, factor: float) -> list[float]:
            values: list[float] = []
            for item in olwr.default_world.sparql(query):
                try:
                    if isinstance(item, list) and len(item) == 1:
                        values.append(float(item[0]) * factor)
                    else:
                        values.append(float(item) * factor)
                except (ValueError, TypeError):
                    logger.warning("Skipped SPARQL item %r", item)
            return values

        # Ensure ontology is loaded into owlready default world
        _ = self.model
        if self._onto is None:
            self.load()

        return {
            "emissionTier1": _scale(SPARQL_TIER1_SUM, gwp / 1000),
            "emissionTier2": _scale(SPARQL_TIER2_SUM, gwp / 1000),
            "milkProduction": _scale(SPARQL_MILK_SUM, 30),
        }

    def period_aggregates(
        self,
        start_month: int,
        start_year: int,
        end_month: int,
        end_year: int,
    ) -> dict[str, Any]:
        df = self.grouped_df.copy()
        # Operational fix: coerce Year/Month to str for datetime construction
        # (original code concatenated ints and failed on some pandas versions).
        df["Date"] = pd.to_datetime(
            df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-1"
        )
        start_date = pd.to_datetime(f"{start_year}-{start_month}-01")
        end_date = pd.to_datetime(f"{end_year}-{end_month}-01")
        filtered = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        yearly = (
            filtered.groupby(["Year"], as_index=False)
            .agg(
                {
                    "Count Dairy Cattle": "mean",
                    "Reference Scenario Emissions Tier 1": "sum",
                    "Reference Scenario Emissions Tier 2": "sum",
                    "Total Milk": "sum",
                }
            )
            .round(2)
        )
        return {
            "Count Dairy Cattle": yearly["Count Dairy Cattle"].tolist(),
            "Reference Scenario Emissions Tier 1": yearly[
                "Reference Scenario Emissions Tier 1"
            ].tolist(),
            "Reference Scenario Emissions Tier 2": yearly[
                "Reference Scenario Emissions Tier 2"
            ].tolist(),
            "Total Milk": yearly["Total Milk"].tolist(),
        }
