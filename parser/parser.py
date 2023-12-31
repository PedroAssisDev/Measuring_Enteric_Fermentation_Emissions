# arquivo_parser.py
import pandas as pd
import numpy as np
import os

from datetime import datetime
'''
Considerações feitas na analise dos dados:
    
    As 3 ordenhas feitas no dia juntas em um 
        groupby(['Date', 'Brinco']).agg({'Leite': 'sum', 'Peso': 'mean'})
    
'''

def parse_file(file_path):
    try:
        # Leitura do arquivo CSV para um DataFrame
        df = pd.read_csv(file_path)

        # Transforma a primeira coluna (Brinco) em string
        df['Brinco'] = df['Brinco'].astype(str)

        # Transforma a segunda coluna (Peso) em float
        df['Peso'] = df['Peso'].apply(parse_to_float)

        # Transforma a terceira coluna (Prod. Leite) em float
        df['Leite'] = df['Leite'].apply(parse_to_float)
        # Converte a quarta coluna (Date) para um objeto datetime
        df['Date'] = df['Date'].apply(parse_date)
        result_df = df.groupby(['Date', 'Brinco']).agg({'Leite': 'sum', 'Peso': 'mean'}).reset_index()
        result_df['Leite'] = result_df['Leite'].round(2)
        result_df['Peso'] = result_df['Peso'].round(2)
        result_df['energyDensity'] = np.round(18+np.random.uniform(-1, 1, size=len(result_df)), 2)
        result_df['dryMatterIntake'] = np.round(25+np.random.uniform(-2, 2, size=len(result_df)), 2)

        current_directory = os.path.dirname(os.path.abspath(__file__))
        base_directory = os.path.dirname(current_directory)
        data_directory = os.path.join(base_directory, "data")
        data_filename = 'pesoXleite_parsed.csv'
        data_filepath = os.path.join(data_directory, data_filename)
        result_df.to_csv(data_filepath, index=False)
        return result_df

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro durante a leitura do arquivo: {e}")
        return None

def parse_date(month):
    # Adiciona o ano de 2021 e define o dia como o último dia do mês
    date = pd.to_datetime(f'2021-{month}-01') + pd.offsets.MonthEnd(0)
    return date

def parse_to_float(value):
    try:
        result = float(value)
        return result
    except ValueError:
        print(f"Erro: Não foi possível converter '{value}' para float.")
        return None
    
# Exemplo de uso
data = print(parse_file(
'/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/data/pesoXleite.csv')) 
# 'data' contém os dados do arquivo CSV com as transformações desejadas


