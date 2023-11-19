# arquivo_parser.py
import pandas as pd
from datetime import datetime


def parse_file(file_path):
    try:
        # Leitura do arquivo CSV para um DataFrame
        df = pd.read_csv(file_path)
        # Transforma a primeira coluna (Brinco) em string
        df['Brinco'] = df['Brinco'].astype(str)

        # Transforma a segunda coluna (Peso) em float
        df['Peso'] = df['Peso'].astype(float)

        # Transforma a terceira coluna (Prod. Leite) em float
        df['Leite'] = df['Leite'].astype(float)

        # Converte a quarta coluna (Date) para um objeto datetime
        df['Date'] = df['Date']
        return df

    except FileNotFoundError:
        print(f"O arquivo {file_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro durante a leitura do arquivo: {e}")
        return None


# Exemplo de uso
# data = print(parse_file(
# '/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/data/dados_vacas.csv')) Agora
# 'data' contém os dados do arquivo CSV com as transformações desejadas
