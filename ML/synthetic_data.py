import numpy as np
import pandas as pd
import os

def generate_synthetic_data(num_samples):
    np.random.seed(42)  
    days = np.random.randint(30, 365, size=num_samples)
    avg_dmi = np.random.uniform(14, 27, size=num_samples)
    energy_density = np.random.uniform(14, 27, size=num_samples)
    avg_heads = np.random.uniform(50, 400, size=num_samples)

    target_variable = (days * avg_dmi *0.01 *energy_density * avg_heads * 6.5 * 20 * 0.001)/55.65

    noise = np.random.normal(-50, 50, size=num_samples)
    target_variable += noise

    return pd.DataFrame({
        'Days': days,
        'Average_DMI': avg_dmi,
        'Energy_density_of_feed': energy_density,
        'Average_number_of_heads': avg_heads,
        'Global_emission_Ton_CO2e': target_variable
    })

num_synthetic_samples = 50000

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
