from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime as dt
from typing import List
from owlready2 import *
import uvicorn

app = FastAPI()

# Carregar a ontologia
onto = get_ontology("/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/ontology/ontologia_final_populada_sync_reasoner_pellet.owl").load()

# Configurar CORS para permitir solicitações de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

@app.get("/total_emissions/period_property")
async def total_emissions_period_property(data_inicio: dt = Query(...), data_fim: dt = Query(...)):
    with onto:
        query = f"""
            SELECT ?total_emissions WHERE {{
                ?property rdf:type :RuralProperty .
                ?property :HasTotalEmissions ?total_emissions .
                ?measurement :measurementDate ?date 
                FILTER(?date >= "{data_inicio.isoformat()}"^^xsd:dateTime && ?date <= "{data_fim.isoformat()}"^^xsd:dateTime) .
                ?measurement :belongs_to_property ?property .
            }}
        """
        results = list(onto.query(query))
        return {'total_emissions': sum(results)}

@app.get("/total_emissions/period_time_group")
async def total_emissions_period_time_group(data_inicio: dt = Query(...), data_fim: dt = Query(...)):
    with onto:
        query = f"""
            SELECT ?grupo ?total_emissions WHERE {{
                ?property rdf:type :RuralProperty .
                ?property :HasCattleGroup ?grupo .
                ?grupo :HasGroupEmissions ?total_emissions .
                ?measurement :measurementDate ?date 
                FILTER(?date >= "{data_inicio.isoformat()}"^^xsd:dateTime && ?date <= "{data_fim.isoformat()}"^^xsd:dateTime) .
                ?measurement :belongs_to_property ?property .
                ?measurement :has_group ?grupo .
            }}
        """
        results = list(onto.query(query))
        return results
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
