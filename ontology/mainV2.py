from rdflib import Graph, Namespace
from calendar import monthrange
from datetime import datetime
import matplotlib.pyplot as plt


def calcular_emissoes_cenario_referencia(emissoes_fator_efeito_estufa, gwp):
    """
    Calcula as emissões no cenário de referência a partir de uma lista de emissões de efeito estufa e o GWP.
    
    Parâmetros:
    - emissoes_fator_efeito_estufa: Lista de emissões de efeito estufa para cada animal/fazenda (em tCO2e).
    - gwp: Potencial de aquecimento global do metano (GWP) em CO2e/kg CH4 (padrão: 1000).
    
    Retorna:
    - Total de emissões no cenário de referência (em tCO2e).
    """
    total_emissoes_cenario_referencia = emissoes_fator_efeito_estufa * gwp / 1000
    return total_emissoes_cenario_referencia


def calcular_fator_emissao_enterico(fatores_emissao_medios, numero_cabecas, dias_no_farm):
    """
    Calcula o fator de emissão entérico para um grupo de animais durante o período de monitoramento.

    Parâmetros:
    - fatores_emissao_medios: Fatores de emissão médios para o grupo de animais (kg CH4 head-1 d-1).
    - numero_cabecas: Número médio de cabeças no grupo de animais na fazenda durante o período de monitoramento.
    - dias_no_farm: Número de dias que cada animal passou na fazenda durante o período de monitoramento.

    Retorna:
    - Fator de emissão entérico para o grupo de animais (em kg CH4).
    """
    fator_emissao_entérico = fatores_emissao_medios * numero_cabecas * dias_no_farm
    return fator_emissao_entérico
  
# Carregar a ontologia RDF
g = Graph()
g.parse("ontology/ontologia_final_populada_sync_reasoner_pellet.owl", format="xml")

# Definir o namespace da ontologia
owl = Namespace("http://www.semanticweb.org/owl/owlapi/mensuring_ontology#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

query_gwp_fator_emissao = """
SELECT ?cattle ?gwp ?fatorEmissao
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:Gwp ?gwp .
  ?cattle owl:fatorEmissao ?fatorEmissao .
}
"""

result_gwp_fator_emissao = g.query(query_gwp_fator_emissao, initNs={"rdf": rdf, "owl": owl})
gwp_array = []
fatorEmissao_array = []
for row in result_gwp_fator_emissao:
    gwp_array.append(int(row.gwp))
    fatorEmissao_array.append(int(row.fatorEmissao))

gwp = sum(gwp_array)/len(gwp_array)
fatorEmissao = sum(fatorEmissao_array)/len(fatorEmissao_array)


# Quantidade de Vaca e Produção Mensal de Leite por Mês/Ano com Último Dia do Mês
query_quantidade_vacas_producao_ultimo_dia = """
SELECT ?month ?year (COUNT(DISTINCT ?cattle) AS ?countDairyCattle) (SUM(?producao) AS ?totalLeite)
                    (AVG(?peso) AS ?pesoMedio) 
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:measurementDate ?date .
  ?measurementData owl:producao ?producao .
  ?measurementData owl:peso ?peso .
  BIND(MONTH(?date) AS ?month)
  BIND(YEAR(?date) AS ?year)
}
GROUP BY ?month ?year 
ORDER BY ?year ?month
"""
# Arrays para armazenar os dados
count_dairy_cattle_array = []
total_leite_array = []
peso_medio_array = []
data_array = []
days_array = []
fator_emissao_enterico_mensal = []
emissoes_cenario_referencia_mensal = []

result_quantidade_vacas_producao_ultimo_dia = g.query(query_quantidade_vacas_producao_ultimo_dia, initNs={"rdf": rdf, "owl": owl})

for row in result_quantidade_vacas_producao_ultimo_dia:
    days = int(monthrange(int(row.year), int(row.month))[1])
    # Armazenar valores nos arrays
    count_dairy_cattle_array.append(int(row.countDairyCattle))
    total_leite_array.append(float(row.totalLeite) * days)
    peso_medio_array.append(float(row.pesoMedio))
    days_array.append(int(days))
    data = datetime(int(row.year), int(row.month), days)
    data_array.append(data)
    fe = calcular_fator_emissao_enterico(fatorEmissao,int(row.countDairyCattle),days)
    cecr = calcular_emissoes_cenario_referencia(fe, gwp)
    fator_emissao_enterico_mensal.append(fe)
    emissoes_cenario_referencia_mensal.append(cecr)
    print("Month:", row.month)
    print("Year:", row.year)
    print("Count Dairy Cattle:", row.countDairyCattle)
    print("Total Leite:", float(row.totalLeite) * days)
    print("Peso Médio:", row.pesoMedio)
    print("Quantidade de dias do Mes", days)
    print("Fator de emissão entérico", fe)
    print("Emissões no cenário de referência", cecr)
    print()



# Criar um subplot com três eixos
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

# Gráfico 1: Quantidade de Vacas e Emissão Entérica por Mês/Ano
color = 'tab:red'
ax1.set_ylabel('Quantidade de Vacas', color=color)
ax1.bar(range(len(data_array)), count_dairy_cattle_array, align="center", color=color, label="Quantidade de Vacas")
ax1.tick_params(axis='y', labelcolor=color)

ax1_2 = ax1.twinx()
color = 'tab:blue'
ax1_2.set_ylabel('Emissão Entérica', color=color)
ax1_2.plot(range(len(data_array)), fator_emissao_enterico_mensal, color=color, marker='o', label="Emissão Entérica")
ax1_2.tick_params(axis='y', labelcolor=color)

# Gráfico 2: Quantidade de Vacas e Cenário de Referência por Mês/Ano
color = 'tab:red'
ax2.set_ylabel('Quantidade de Vacas', color=color)
ax2.bar(range(len(data_array)), count_dairy_cattle_array, align="center", color=color, label="Quantidade de Vacas")
ax2.tick_params(axis='y', labelcolor=color)

ax2_2 = ax2.twinx()
color = 'tab:green'
ax2_2.set_ylabel('Cenário de Referência', color=color)
ax2_2.plot(range(len(data_array)), emissoes_cenario_referencia_mensal, color=color, marker='o', label="Cenário de Referência")
ax2_2.tick_params(axis='y', labelcolor=color)

# Gráfico 3: Quantidade de Vacas, Produção Total de Leite e Cenário de Referência por Mês/Ano
color = 'tab:red'
ax3.set_xlabel('Data')
ax3.set_ylabel('Quantidade de Vacas', color=color)
ax3.bar(range(len(data_array)), count_dairy_cattle_array, align="center", color=color, label="Quantidade de Vacas")
ax3.tick_params(axis='y', labelcolor=color)

ax3_2 = ax3.twinx()
color = 'tab:blue'
ax3_2.set_ylabel('Produção Total de Leite', color=color)
ax3_2.plot(range(len(data_array)), total_leite_array, color=color, marker='o', label="Produção Total de Leite")
ax3_2.tick_params(axis='y', labelcolor=color)

ax3_3 = ax3.twinx()
color = 'tab:green'
ax3_3.spines['right'].set_position(('outward', 60))
ax3_3.set_ylabel('Cenário de Referência', color=color)
ax3_3.plot(range(len(data_array)), emissoes_cenario_referencia_mensal, color=color, marker='o', label="Cenário de Referência")
ax3_3.tick_params(axis='y', labelcolor=color)

# Ajustar layout
fig.tight_layout()  

# Adicionar título
plt.suptitle("Comparação: Quantidade de Vacas, Emissão Entérica, Produção Total de Leite e Cenário de Referência por Mês/Ano", y=0.96)

# Exibir o gráfico
plt.show()


# Gráfico de barras para a quantidade de vacas por mês/ano
plt.figure(figsize=(10, 6))
plt.bar(range(len(data_array)), count_dairy_cattle_array, align="center")
plt.xticks(range(len(data_array)), [f"{data.month}/{data.year}" for data in data_array], rotation=45)
plt.title("Quantidade de Vacas por Mês/Ano")
plt.xlabel("Data")
plt.ylabel("Quantidade de Vacas")
plt.tight_layout()
plt.grid()
plt.show()

# Gráfico de barras para a produção total de leite por mês/ano
plt.figure(figsize=(10, 6))
plt.bar(range(len(data_array)), total_leite_array, align="center")
plt.xticks(range(len(data_array)), [f"{data.month}/{data.year}" for data in data_array], rotation=45)
plt.title("Produção Total de Leite por Mês/Ano")
plt.xlabel("Data")
plt.ylabel("Produção Total de Leite (tCO2e)")
plt.tight_layout()
plt.grid()
plt.show()

# Gráfico de linha para o peso médio por mês/ano
plt.figure(figsize=(10, 6))
plt.plot(range(len(data_array)), peso_medio_array, marker='o')
plt.xticks(range(len(data_array)), [f"{data.month}/{data.year}" for data in data_array], rotation=45)
plt.title("Peso Médio por Mês/Ano")
plt.xlabel("Data")
plt.ylabel("Peso Médio")
plt.tight_layout()
plt.grid()
plt.show()

# Gráfico de barras para as emissões no cenário de referência por mês/ano
plt.figure(figsize=(10, 6))
plt.bar(range(len(data_array)), emissoes_cenario_referencia_mensal, align="center")
plt.xticks(range(len(data_array)), [f"{data.month}/{data.year}" for data in data_array], rotation=45)
plt.title("Emissões no Cenário de Referência por Mês/Ano")
plt.xlabel("Data")
plt.ylabel("Emissões no Cenário de Referência (tCO2e)")
plt.tight_layout()
plt.grid()
plt.show()

# Gráfico de barras para o fator de emissão entérico por mês/ano
plt.figure(figsize=(10, 6))
plt.bar(range(len(data_array)), fator_emissao_enterico_mensal, align="center")
plt.xticks(range(len(data_array)), [f"{data.month}/{data.year}" for data in data_array], rotation=45)
plt.title("Fator de Emissão Entérico por Mês/Ano")
plt.xlabel("Data")
plt.ylabel("Fator de Emissão Entérico (kg CH4)")
plt.tight_layout()
plt.grid()
plt.grid()
plt.show()