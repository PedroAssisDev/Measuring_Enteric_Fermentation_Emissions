import pandas as pd
from datetime import datetime, timedelta
import random

# Função para gerar dados para uma vaca em um intervalo de dias
def generate_data(brinco, start_date, num_days):
    data = []
    for i in range(num_days):
        date = start_date + timedelta(days=i)
        peso = round(random.uniform(700, 800), 2)
        prod_leite = round(random.uniform(25, 45), 2)
        data.append((brinco, peso, prod_leite, date))
    return data

# Gerar dados para 100 vacas, um por dia, ao longo do ano de 2021
num_vacas = 3
start_date = datetime(2021, 1, 1)
num_days = 365

all_vacas_data = []

for vaca_id in range(1, num_vacas + 1):
    vaca_data = generate_data(vaca_id, start_date, num_days)
    all_vacas_data.extend(vaca_data)

# Criar DataFrame usando pandas
df = pd.DataFrame(all_vacas_data, columns=["Brinco", "Peso", "Leite", "Date"])

# Especificar o diretório de destino
output_directory = "/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/data/"

# Criar o caminho completo do arquivo CSV
output_file_path = f"{output_directory}/Fazenda_Abc_dados_vacas.csv"

# Salvar o DataFrame em um arquivo CSV no diretório especificado
df.to_csv(output_file_path, index=False)

print(f"Dados gerados e salvos em {output_file_path}")
