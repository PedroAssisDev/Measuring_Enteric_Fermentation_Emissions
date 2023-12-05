from rdflib import Graph, Namespace
from calendar import calendar, monthrange
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import os
import numpy as np


current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ml_directory = os.path.join(base_directory, "ML")
model_filename = 'linear_regression_model.pkl'
model_filepath = os.path.join(ml_directory, model_filename)
linear_model = joblib.load(model_filepath)
ontology_directory = os.path.join(base_directory, "ontology/ontologia_populada_sync_reasoner_pellet.owl")
g = Graph()
g.parse(ontology_directory, format="xml")

new_data = pd.DataFrame({
    'Days': [170],
    'Average_DMI': [24.66],
    'Energy_density_of_feed': [18.45],
    'Average_number_of_heads': [260.07]
})

predictions = linear_model.predict(new_data)

print("Predictions:")
print(f'Total emissions in the predictions scenario {float(predictions[0])} tCO2')
62317.10362901166

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


def calculate_enteric_emission_factor(average_emission_factors, number_of_heads, days_on_farm):
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


query_number_of_cows_milk_production_last_day = """
SELECT ?month ?year (COUNT(DISTINCT ?cattle) AS ?countDairyCattle) (SUM(?milkProduction) AS ?totalMilk)
                    (AVG(?weight) AS ?averageWeight) 
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:measurementDate ?date .
  ?measurementData owl:milkProduction ?milkProduction .
  ?measurementData owl:weight ?weight .
  BIND(MONTH(?date) AS ?month)
  BIND(YEAR(?date) AS ?year)
}
GROUP BY ?month ?year 
ORDER BY ?year ?month
"""
df = pd.DataFrame(columns=['Month', 'Year', 'Count Dairy Cattle', 'Total Milk', 'Average Weight', 'Number of days', 'Enteric Emission Factor', 'Reference Scenario Emissions'])

result_number_of_cows_milk_production_last_day = g.query(query_number_of_cows_milk_production_last_day, initNs={"rdf": rdf, "owl": owl})

data = []  

for row in result_number_of_cows_milk_production_last_day:
    days = int(monthrange(int(row.year), int(row.month))[1])

    count_dairy_cattle = int(row.countDairyCattle)
    total_milk = float(row.totalMilk) * days
    average_weight = float(row.averageWeight)
    date = datetime(int(row.year), int(row.month), days)
    enteric_ef = calculate_enteric_emission_factor(emissionFactorTier1, count_dairy_cattle, days)
    reference_scenario_emissions = calculate_reference_scenario_emissions(enteric_ef, gwp)

    data.append([row.month, row.year, count_dairy_cattle, total_milk, average_weight, days, enteric_ef, reference_scenario_emissions])

df = pd.concat([df, pd.DataFrame(data, columns=df.columns)], ignore_index=True)

print(df)


df_grouped = df.groupby(['Year', 'Month']).agg({
    'Count Dairy Cattle': 'sum',
    'Reference Scenario Emissions': 'sum'
}).reset_index()

df_grouped = df_grouped.sort_values(['Year', 'Month'])

month_names = [f"{month}-{year}" for year, month in zip(df_grouped['Year'], df_grouped['Month'])]

fig, ax = plt.subplots(figsize=(24, 12))

bar_width = 0.4
bar_positions = np.arange(len(df_grouped))
ax.bar(bar_positions - bar_width/2, df_grouped['Count Dairy Cattle'], width=bar_width, align="center", label="Number of Cows", color='tab:red')
ax.set_ylabel('Number of Cows', color='tab:red')
ax.tick_params(axis='y', labelcolor='tab:red')

ax_2 = ax.twinx()
ax_2.bar(bar_positions + bar_width/2, df_grouped['Reference Scenario Emissions'], width=bar_width, align="center", label="Total Emissions", color='tab:blue')
ax_2.set_ylabel('Total Emissions (tCO2e)', color='tab:blue')
ax_2.tick_params(axis='y', labelcolor='tab:blue')

ax.set_xticks(bar_positions)
ax.set_xticklabels(month_names, rotation=45, ha='right')

lines, labels = ax.get_legend_handles_labels()
lines_2, labels_2 = ax_2.get_legend_handles_labels()
ax.legend(lines + lines_2, labels + labels_2, loc='upper right')

ax.grid(axis='y', linestyle='--', alpha=0.7)

fig.tight_layout()

plt.title("Number of Cows and Total Emissions in the Reference Scenario")

plt.show()


(fig, (ax1, ax2)) = plt.subplots(nrows=2, sharex=True, figsize=(12, 10))

bar_width = 0.4
bar_positions = np.arange(len(df_grouped))

ax1.bar(bar_positions - bar_width/2, df_grouped['Count Dairy Cattle'], width=bar_width, align="center", label="Number of Cows", color='tab:red')
ax1.set_ylabel('Number of Cows', color='tab:red', fontsize=20)  # Ajuste o tamanho da fonte aqui
ax1.tick_params(axis='y', labelcolor='tab:red')

ax2.bar(bar_positions + bar_width/2, df_grouped['Reference Scenario Emissions'], width=bar_width, align="center", label="Total Emissions", color='tab:blue')
ax2.set_ylabel('Total Emissions (tCO2e)', color='tab:blue', fontsize=20)  # Ajuste o tamanho da fonte aqui
ax2.tick_params(axis='y', labelcolor='tab:blue')

ax2.set_xticks(bar_positions)
ax2.set_xticklabels(month_names, rotation=45, ha='right', fontsize=20)  # Ajuste o tamanho da fonte aqui

lines, labels = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines, labels, loc='upper right', fontsize=20)  # Ajuste o tamanho da fonte aqui
ax2.legend(lines_2, labels_2, loc='upper right', fontsize=20)  # Ajuste o tamanho da fonte aqui

ax1.grid(axis='y', linestyle='--', alpha=0.7)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

fig.tight_layout()

fig.suptitle("Number of Cows and Total Emissions in the Reference Scenario", y=1.02, fontsize=22)  # Ajuste o tamanho da fonte aqui

plt.show()