from rdflib import Graph, Namespace
from calendar import monthrange
from datetime import datetime
import pandas as pd
import joblib
import os
import owlready2 as olwr
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# python3 -m streamlit run dashboard.py

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ml_directory = os.path.join(base_directory, "ML")
model_filename = 'linear_regression_model.pkl'
model_filepath = os.path.join(ml_directory, model_filename)
linear_model = joblib.load(model_filepath)
ontology_directory = os.path.join(base_directory, "ontology/ontologia_populada_sync_reasoner_pellet.owl")
onto = olwr.get_ontology(ontology_directory).load()

g = Graph()
g.parse(ontology_directory, format="xml")

def predict_model(days, dmi, energy, heads):
    new_data = pd.DataFrame({
        'Days': [days],
        'Average_DMI': [dmi],
        'Energy_density_of_feed': [energy],
        'Average_number_of_heads': [150]
    })

    return linear_model.predict(new_data)


def calculate_reference_scenario_emissions(greenhouse_gas_emissions, gwp):
    """
    Calculates emissions in the reference scenario from a list of greenhouse gas emissions and the global warming potential (gwp).
    
    Parameters:
    - greenhouse_gas_emissions: List of greenhouse gas emissions for each animal/farm (in tCO2e).
    - gwp: Global Warming Potential of methane (gwp) in CO2e/kg CH4.
    
    Returns:
    - Total emissions in the reference scenario (in tCO2e).
    """
    total_reference_scenario_emissions = greenhouse_gas_emissions * gwp / 1000
    return total_reference_scenario_emissions


def calculate_enteric_emission_factor_tier1(average_emission_factors, number_of_heads, days_on_farm):
    """
    Calculates the enteric emission factor for a group of animals during the monitoring period.

    Parameters:
    - average_emission_factors: Average emission factors for the group of animals (kg CH4 head-1 d-1).
    - number_of_heads: Average number of heads in the group of animals on the farm during the monitoring period.
    - days_on_farm: Number of days each animal spent on the farm during the monitoring period.

    Returns:
    - Enteric emission factor for the group of animals (in kg CH4).
    """
    enteric_emission_factor = average_emission_factors * number_of_heads * days_on_farm
    return enteric_emission_factor

def calculate_enteric_emission_factor_tier2(averageEnergyDensity, averageDryMatterIntake, averageEmissionFactorTier2, number_of_heads, days_on_farm):
    enteric_emission_factor = averageEnergyDensity* averageDryMatterIntake* averageEmissionFactorTier2 * number_of_heads * days_on_farm *  0.01
    return enteric_emission_factor/55.65
  

owl = Namespace("http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


query_gwp_emission_factor = """
SELECT ?cattle ?gwp ?emissionFactorTier1
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:gwp ?gwp .
  ?cattle owl:emissionFactorTier1 ?emissionFactorTier1 .
}
"""

result_gwp_emission_factor = g.query(query_gwp_emission_factor, initNs={"rdf": rdf, "owl": owl})
gwp_array = []
emissionFactorTier1_array = []
for row in result_gwp_emission_factor:
    gwp_array.append(float(row.gwp))
    emissionFactorTier1_array.append(float(row.emissionFactorTier1))

gwp = sum(gwp_array)/len(gwp_array)
emissionFactorTier1 = sum(emissionFactorTier1_array)/len(emissionFactorTier1_array)



query_number_of_cows_milk_production = """
SELECT ?month ?year (COUNT(DISTINCT ?cattle) AS ?countDairyCattle) (SUM(?milkProduction) AS ?totalMilk)
                    (AVG(?weight) AS ?averageWeight)  (AVG(?energyDensity) AS ?averageEnergyDensity) (AVG(?dryMatterIntake) AS ?averageDryMatterIntake) (AVG(?emissionFactorTier2) AS ?averageEmissionFactorTier2)
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
df = pd.DataFrame(columns=['Month', 'Year', 'Count Dairy Cattle', 'Total Milk', 'Average Weight', 'Number of days', 'Enteric Emission Factor Tier 1', 'Reference Scenario Emissions Tier 1', 
                           'Enteric Emission Factor Tier 2', 'Reference Scenario Emissions Tier 2'])

result_number_of_cows_milk_production_last_day = g.query(query_number_of_cows_milk_production, initNs={"rdf": rdf, "owl": owl})

data = []  

for row in result_number_of_cows_milk_production_last_day:
    days = int(monthrange(int(row.year), int(row.month))[1])

    count_dairy_cattle = int(row.countDairyCattle)
    total_milk = float(row.totalMilk) * days
    average_weight = float(row.averageWeight)
    date = datetime(int(row.year), int(row.month), days)
    enteric_ef_tier1 = calculate_enteric_emission_factor_tier1(emissionFactorTier1, count_dairy_cattle, days)
    reference_scenario_emissions_tier1 = calculate_reference_scenario_emissions(enteric_ef_tier1, gwp)
    averageEnergyDensity = float(row.averageEnergyDensity)
    averageDryMatterIntake = float(row.averageDryMatterIntake)
    averageEmissionFactorTier2 = float(row.averageEmissionFactorTier2)
    enteric_ef_tier2 = calculate_enteric_emission_factor_tier2(averageEnergyDensity, averageDryMatterIntake, averageEmissionFactorTier2, count_dairy_cattle, days)
    reference_scenario_emissions_tier2 = calculate_reference_scenario_emissions(enteric_ef_tier2, gwp)

    data.append([row.month, row.year, count_dairy_cattle, total_milk, average_weight, days, enteric_ef_tier1, reference_scenario_emissions_tier1,
                 enteric_ef_tier2, reference_scenario_emissions_tier2])

df = pd.DataFrame(data, columns=df.columns)


st.set_page_config(layout="wide")
st.sidebar.subheader("Predictions")

days_input = st.sidebar.number_input("Days:", min_value=0, max_value=900, value= 0)
dmi_input = st.sidebar.number_input("Average DMI:", min_value=0, value=0)
energy_input = st.sidebar.number_input("Energy Density of Feed:", min_value=0, value = 0)
heads_input = st.sidebar.number_input("Average Number of Heads:", min_value=0, value = 0)

if st.sidebar.button("Projected Scenario"):
    prediction = float(predict_model(days_input, dmi_input, energy_input, heads_input))
    if prediction < 0:
        st.sidebar.error(f"The provided values don't make sense.")
    else:
        st.sidebar.success(f"Estimated total emissions in the projected scenario: {prediction} tons of CO2")


df["Date"] = df["Month"].astype(str) + "-" + df["Year"].astype(str)

df["Date"] = pd.to_datetime(df["Date"])

df.to_csv("test.csv", sep= ";")

start_month = st.sidebar.selectbox("Start Month", df["Date"].dt.strftime("%m-%Y").unique())
last_month = st.sidebar.selectbox("End Month", df["Date"].dt.strftime("%m-%Y").unique())

start_month = pd.to_datetime(start_month, format="%m-%Y")
last_month = pd.to_datetime(last_month, format="%m-%Y")

df_filtered = df[(df["Date"] >= start_month) & (df["Date"] <= last_month)]

st.title("Milk Production and Emissions Analysis")

# Line chart for total milk production over time
fig1 = px.line(df_filtered, x="Date", y="Total Milk", title="Total Milk Production Over Time")
fig1.update_yaxes(title_text='Milk Production [L]')  # Add this line to set the y-axis label
st.plotly_chart(fig1, use_container_width=True)

# Bar chart for the average number of dairy cattle
fig2 = px.bar(df_filtered, x="Date", y="Count Dairy Cattle", title="Average Number of Dairy Cattle Over Time")
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(df_filtered, x="Date", y=["Reference Scenario Emissions Tier 1"],
               title="Reference Scenario Emissions Tier 1")
fig3.update_yaxes(title_text='CO2 Emissions [tons]')  # Add this line to set the y-axis label
st.plotly_chart(fig3, use_container_width=True)

# Stacked bar chart for enteric emissions Tier 1 and Tier 2
fig4 = px.bar(df_filtered, x="Date", y=["Enteric Emission Factor Tier 1"],
              title="Enteric Emissions Tier 1")
fig4.update_yaxes(title_text='CH4 Emissions [kg]')  # Add this line to set the y-axis label
st.plotly_chart(fig4, use_container_width=True)
