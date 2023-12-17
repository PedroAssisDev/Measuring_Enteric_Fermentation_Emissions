from fastapi import FastAPI
import uvicorn
from rdflib import Graph, Namespace
from calendar import calendar, monthrange
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import os
import numpy as np
import owlready2 as olwr

app = FastAPI()

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ml_directory = os.path.join(base_directory, "ML")
model_filename = 'linear_regression_model.pkl'
model_filepath = os.path.join(ml_directory, model_filename)
linear_model = joblib.load(model_filepath)
ontology_directory = os.path.join(base_directory, "ontology/ontologia_populada_sync_reasoner_pellet.owl")
onto = olwr.get_ontology(ontology_directory).load()

olwr.sync_reasoner_pellet(infer_data_property_values=True, infer_property_values=True)


calc_query_tier1_aux = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?totalIndividualEntericEmissionFactorTier1) AS ?totalSum)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:totalIndividualEntericEmissionFactorTier1 ?totalIndividualEntericEmissionFactorTier1 .
}
"""
calc_query_tier2_aux = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?totalIndividualEntericEmissionFactorTier2) AS ?totalSum)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:totalIndividualEntericEmissionFactorTier2 ?totalIndividualEntericEmissionFactorTier2 .
}
"""
calc_query_milk_aux = """
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

g = Graph()
g.parse(ontology_directory, format="xml")


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
    """
    
    """
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

df = pd.concat([df, pd.DataFrame(data, columns=df.columns)], ignore_index=True)

tot_reference_scenario_emissions1 = df["Reference Scenario Emissions Tier 1"].sum()
tot_reference_scenario_emissions2 = df["Reference Scenario Emissions Tier 2"].sum()

#print("Reference Scenario:")
#print(f'Total emissions in the reference scenario 1 {float(tot_reference_scenario_emissions1)} tCO2')
#print(f'Total emissions in the reference scenario 2 {float(tot_reference_scenario_emissions2)} tCO2')

df_grouped = df.groupby(['Year', 'Month']).agg({
    'Count Dairy Cattle': 'sum',
    'Number of days': 'mean', 
    'Total Milk': 'sum',
    'Enteric Emission Factor Tier 1': 'sum', 
    'Reference Scenario Emissions Tier 1': 'sum', 
    'Enteric Emission Factor Tier 2': 'sum', 
    'Reference Scenario Emissions Tier 2': 'sum'
    
}).reset_index()

df_grouped = df_grouped.sort_values(['Year', 'Month'])

#print(df_grouped)
#df_grouped.to_csv('/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/src/aaa.csv', sep=';', index=False)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/prod/totalYear/")
def read_item(aux: int):
    result_query_milk = olwr.default_world.sparql(calc_query_milk_aux)
    result_multiplied_milk = []
    for item in result_query_milk:
        try:
            if isinstance(item, list) and len(item) == 1:
                result_multiplied_milk.append(float(item[0]) * 30)
            else:
                result_multiplied_milk.append(float(item) * 30)
        except (ValueError, TypeError):
            print(f"Warning: Skipped item {item} in result_query_milk")
    result_query_tier1 = olwr.default_world.sparql(calc_query_tier1_aux)
    result_multiplied_tier1 = []
    for item in result_query_tier1:
        try:
            if isinstance(item, list) and len(item) == 1:
                result_multiplied_tier1.append(float(item[0]) * 28.00 / 1000)
            else:
                result_multiplied_tier1.append(float(item) * 28.00 / 1000)
        except (ValueError, TypeError):
            print(f"Warning: Skipped item {item} in result_query_tier1")
    result_query_tier2 = olwr.default_world.sparql(calc_query_tier2_aux)
    result_multiplied_tier2 = []
    for item in result_query_tier2:
        try:
            if isinstance(item, list) and len(item) == 1:
                result_multiplied_tier2.append(float(item[0]) * 28.00 / 1000)
            else:
                result_multiplied_tier2.append(float(item) * 28.00 / 1000)
        except (ValueError, TypeError):
            print(f"Warning: Skipped item {item} in result_query_tier2")

    return {
        "emissionTier1": result_multiplied_tier1, 
        "emissionTier2":  result_multiplied_tier2,
        "milkProduction": result_multiplied_milk
        }

@app.get("/prod/Predictions/")
def read_item(days: float, 
              average_DMI: float,
              energy_density_of_feed: float,
              average_number_of_heads: float):
    new_data = pd.DataFrame({
    'Days': [days],
    'Average_DMI': [average_DMI],
    'Energy_density_of_feed': [energy_density_of_feed],
    'Average_number_of_heads': [average_number_of_heads]
    })
    predictions = linear_model.predict(new_data)
    #print(predictions)
    return {
        "Predictions scenario": list(predictions)
        }


@app.get("/prod/period/")
def period(start_month: int, 
                 start_year: int,
                 end_month: int, 
                 end_year: int):
    df = df_grouped.copy()
    df['Date'] = pd.to_datetime(df['Year']+'-'+ df['Month']+'-'+ "1")

    # Definir as datas de início e término desejadas
    start_date = pd.to_datetime(f'{start_year}-{start_month}-01')
    end_date = pd.to_datetime(f'{end_year}-{end_month}-01')

    # Filtrar o DataFrame para o intervalo desejado
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Agrupar por ano e mês e calcular as médias
    df = filtered_df.groupby(['Year']).agg({
        'Count Dairy Cattle': 'mean',
        'Reference Scenario Emissions Tier 1': 'sum',
        'Reference Scenario Emissions Tier 2': 'sum',
        'Total Milk': 'sum',
        

    }).reset_index()

    df = df.round(2)
    return{
        "Count Dairy Cattle": df['Count Dairy Cattle'],
        "Reference Scenario Emissions Tier 1": df['Reference Scenario Emissions Tier 1'],
        "Reference Scenario Emissions Tier 2": df['Reference Scenario Emissions Tier 2'],
        "Total Milk": df['Total Milk']
        }




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
