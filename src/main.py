import os
from ontology.ontology import *


fileName = r"ontologia_populada.owl"
# Exemplo de chamada da função
if os.path.isfile(fileName):
    print("Loading OWL file...")
else:
    popula_ontologia()

