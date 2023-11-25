# arquivo_parser.py
import pandas as pd
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
        result_df.to_csv('/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/data/pesoXleite_parsed.csv', index=False)
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
