from rdflib import Graph, Namespace

# Carregar a ontologia RDF
g = Graph()
g.parse("ontology/ontologia_populada_sync_reasoner_pellet.owl", format="xml")

# Definir o namespace da ontologia
owl = Namespace("http://www.semanticweb.org/owl/owlapi/mensuring_ontology#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")



# Exemplo de consulta SPARQL para encontrar todos os indivíduos do tipo 'DairyCattle'
query_dairy_cattle = """
SELECT ?cattle
WHERE {
  ?cattle rdf:type owl:DairyCattle .
}
"""

# Executar a consulta
result_dairy_cattle = g.query(query_dairy_cattle, initNs={"rdf": rdf, "owl": owl})

# Imprimir os resultados
for row in result_dairy_cattle:
    print("DairyCattle:", row.cattle)
    
    
# Exemplo de consulta SPARQL para contar o número de instâncias de DairyCattle
query_count_dairy_cattle = """
SELECT (COUNT(?cattle) AS ?countDairyCattle)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
}
"""

# Executar a consulta
result_count_dairy_cattle = g.query(query_count_dairy_cattle, initNs={"rdf": rdf, "owl": owl})

# Imprimir os resultados
for row in result_count_dairy_cattle:
    print("Número de DairyCattle:", row.countDairyCattle)
    

# Exemplo de consulta SPARQL para obter o total produzido por cada vaca
query_total_producao_por_vaca = """
SELECT ?cattle (SUM(?producao) AS ?totalProducao)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:producao ?producao .
}
GROUP BY ?cattle
"""

# Executar a consulta
result_total_producao_por_vaca = g.query(query_total_producao_por_vaca, initNs={"rdf": rdf, "owl": owl})

# Imprimir os resultados
for row in result_total_producao_por_vaca:
    print("Vaca:", row.cattle)
    print("Total de Produção:", row.totalProducao)

# Exemplo de consulta SPARQL para obter o total produzido e peso médio por vaca e mês
query_total_producao_peso_por_vaca_mes = """
SELECT ?cattle ?mes (SUM(?producao) AS ?totalProducao) (AVG(?peso) AS ?pesoMedio)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:producao ?producao .
  ?measurementData owl:peso ?peso .
  ?measurementData owl:measurementDate ?dataMedicao .
  BIND(MONTH(?dataMedicao) AS ?mes)
}
GROUP BY ?cattle ?mes
"""

# Executar a consulta
result_total_producao_peso_por_vaca_mes = g.query(query_total_producao_peso_por_vaca_mes, initNs={"rdf": rdf, "owl": owl})

# Imprimir os resultados
for row in result_total_producao_peso_por_vaca_mes:
    print("Vaca:", row.cattle)
    print("Mês:", row.mes)
    print("Total de Produção:", row.totalProducao)
    print("Peso Médio:", row.pesoMedio)
    print()
    
# Exemplo de consulta SPARQL para obter o total produzido e peso médio por vaca e mês
query_total_producao_peso_por_vaca_mes = """
SELECT ?cattle ?mes (SUM(?producao) AS ?totalProducao) (AVG(?peso) AS ?pesoMedio)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:producao ?producao .
  ?measurementData owl:peso ?peso .
  ?measurementData owl:measurementDate ?dataMedicao .
  BIND(MONTH(?dataMedicao) AS ?mes)
}
GROUP BY ?cattle ?mes
"""

# Executar a consulta
result_total_producao_peso_por_vaca_mes = g.query(query_total_producao_peso_por_vaca_mes, initNs={"rdf": rdf, "owl": owl})

# Imprimir os resultados
for row in result_total_producao_peso_por_vaca_mes:
    print("Vaca:", row.cattle)
    print("Mês:", row.mes)
    print("Total de Produção:", row.totalProducao)
    print("Peso Médio:", row.pesoMedio)
    print()

# 1. Produção Total de Leite por Vaca
query_producao_total = """
SELECT ?cattle (SUM(?producao) AS ?totalLeite)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:producao ?producao .
}
GROUP BY ?cattle
"""

result_producao_total = g.query(query_producao_total, initNs={"rdf": rdf, "owl": owl})

for row in result_producao_total:
    print("DairyCattle:", row.cattle)
    print("Total Leite:", row.totalLeite)
    print()
    
# Quantidade de Vaca por Mês/Ano
query_quantidade_vacas = """
SELECT ?month ?year (COUNT(DISTINCT ?cattle) AS ?countDairyCattle)
WHERE {
  ?cattle rdf:type owl:DairyCattle .
  ?cattle owl:HasMeasurementData ?measurementData .
  ?measurementData owl:measurementDate ?date .
  BIND(MONTH(?date) AS ?month)
  BIND(YEAR(?date) AS ?year)
}
GROUP BY ?month ?year
"""

result_quantidade_vacas = g.query(query_quantidade_vacas, initNs={"rdf": rdf, "owl": owl})

for row in result_quantidade_vacas:
    print("Month:", row.month)
    print("Year:", row.year)
    print("Count Dairy Cattle:", row.countDairyCattle)
    print()