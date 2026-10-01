"""Streamlit dashboard for milk production and enteric emission analysis."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from carbonseco_livestock.config import get_project_paths
from carbonseco_livestock.ml import predict_emissions
from carbonseco_livestock.ontology import build_monthly_emissions_dataframe
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)


def run_dashboard() -> None:
    paths = get_project_paths()
    df = build_monthly_emissions_dataframe(include_diet_columns=True)

    st.set_page_config(layout="wide")
    st.sidebar.subheader("Predictions")

    days_input = st.sidebar.number_input("Days:", min_value=0)
    dmi_input = st.sidebar.number_input("Average DMI:", min_value=0)
    energy_input = st.sidebar.number_input("Energy Density of Feed:", min_value=0)
    heads_input = st.sidebar.number_input("Average Number of Heads:", min_value=0)

    if st.sidebar.button("Projected Scenario"):
        logger.info("Projection request heads=%s type=%s", heads_input, type(heads_input))
        prediction = predict_emissions(
            float(days_input),
            float(dmi_input),
            float(energy_input),
            float(heads_input),
        )
        if prediction < 0:
            st.sidebar.error("The provided values don't make sense.")
        else:
            st.sidebar.success(
                f"Estimated total emissions in the projected scenario: "
                f"{round(prediction, 2)} tons of CO2"
            )

    df = df.copy()
    df["Date"] = pd.to_datetime(
        df["Month"].astype(str) + "-" + df["Year"].astype(str),
        format="%m-%Y",
    )

    export_path = paths.results / "monthly_emissions_export.csv"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(export_path, sep=";", index=False)

    start_month = st.sidebar.selectbox(
        "Start Month", df["Date"].dt.strftime("%m-%Y").unique()
    )
    last_month = st.sidebar.selectbox(
        "End Month",
        df["Date"].dt.strftime("%m-%Y").unique(),
        index=min(2, len(df) - 1),
    )

    start_month_dt = pd.to_datetime(start_month, format="%m-%Y")
    last_month_dt = pd.to_datetime(last_month, format="%m-%Y")
    df_filtered = df[(df["Date"] >= start_month_dt) & (df["Date"] <= last_month_dt)]

    st.title("Milk Production and Emissions Analysis")

    total_period_milk = df_filtered["Total Milk"].sum()
    formatted_start = start_month_dt.strftime("%Y-%m")
    formatted_end = last_month_dt.strftime("%Y-%m")

    fig1 = px.line(
        df_filtered,
        x="Date",
        y="Total Milk",
        title=(
            f"Total Milk for {formatted_start} to {formatted_end}: "
            f"{total_period_milk:.2f} Liters."
        ),
    )
    fig1.update_yaxes(title_text="Milk Production [L]")
    st.plotly_chart(fig1, use_container_width=True)

    total_period_cattle = df_filtered["Count Dairy Cattle"].mean()
    fig2 = px.bar(
        df_filtered,
        x="Date",
        y="Count Dairy Cattle",
        title=(
            f"Average Number of Dairy Cattle for {formatted_start} to {formatted_end}: "
            f"{total_period_cattle:.2f} Cattle."
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)

    total_tier1 = df_filtered["Reference Scenario Emissions Tier 1"].sum()
    fig3 = px.bar(
        df_filtered,
        x="Date",
        y="Reference Scenario Emissions Tier 1",
        title=(
            f"Total Reference Scenario Emissions Tier 1 for {formatted_start} to "
            f"{formatted_end}: {total_tier1:.2f} tons of CO2."
        ),
    )
    fig3.update_yaxes(title_text="CO2 Emissions [tons]")
    st.plotly_chart(fig3, use_container_width=True)

    total_tier2 = df_filtered["Reference Scenario Emissions Tier 2"].sum()
    fig4 = px.bar(
        df_filtered,
        x="Date",
        y="Reference Scenario Emissions Tier 2",
        title=(
            f"Total Reference Scenario Emissions Tier 2 for {formatted_start} to "
            f"{formatted_end}: {total_tier2:.2f} tons of CO2."
        ),
    )
    fig4.update_yaxes(title_text="CO2 Emissions [tons]")
    st.plotly_chart(fig4, use_container_width=True)


if __name__ == "__main__":
    run_dashboard()
