import numpy as np
import pandas as pd
import os

def generate_synthetic_data(num_samples):
    np.random.seed(42)  
    days = np.random.randint(90, 1000, size=num_samples)
    avg_dmi = np.random.uniform(14, 27, size=num_samples)
    energy_density = np.random.uniform(18, 19.5, size=num_samples)
    avg_heads = np.random.uniform(100, 500, size=num_samples)

    target_variable = (days * avg_dmi*6.5 *0.01 *energy_density * avg_heads*28*0.01) * np.random.uniform(2, 3, size=num_samples)

    noise = np.random.normal(0, 100, size=num_samples)
    target_variable += noise

    return pd.DataFrame({
        'Days': days,
        'Average_DMI': avg_dmi,
        'Energy_density_of_feed': energy_density,
        'Average_number_of_heads': avg_heads,
        'Global_emission_Ton_CO2e': target_variable
    })

num_synthetic_samples = 100000

synthetic_data = generate_synthetic_data(num_synthetic_samples)

print(synthetic_data.head())

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ml_directory = os.path.join(base_directory, "ML")
data_directory = os.path.join(ml_directory, "sintetico.csv")

if not os.path.exists(ml_directory):
    os.makedirs(ml_directory)

synthetic_data.to_csv(data_directory, index=False)

print(f'Dados sintéticos salvos em: {data_directory}')
