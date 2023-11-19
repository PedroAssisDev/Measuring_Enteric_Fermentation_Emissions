from owlready2 import *

def calculate_baseline_emissions_from_ontology(onto, farm_instance):
    """
    Calcula as emissões de metano na situação de referência para uma fazenda representada na ontologia.

    Parâmetros:
    - onto: A ontologia carregada com os dados.
    - farm_instance: Instância da classe RuralProperty representando a fazenda.

    Retorna:
    - Emissões totais de metano na situação de referência para a fazenda.
    """
    total_emissions = 0

    # Obtém os dados da fazenda da ontologia
    groups_on_farm = onto.HasCattleGroup[farm_instance]

    # Itera sobre cada grupo de animais na fazenda
    for group_instance in groups_on_farm:
        # Extrai dados do grupo de animais
        ef_i = group_instance.HasGroupEmissions[0]  # Fator de emissão médio do grupo
        days_i = group_instance.daysOnFarm[0]  # Número de dias que cada animal passou na fazenda
        n_i = group_instance.HasAnimalQuantity[0]  # Número médio de animais no grupo na fazenda

        # Calcula as emissões para o grupo atual
        emissions_i = ef_i * n_i * days_i

        # Adiciona as emissões do grupo ao total
        total_emissions += emissions_i

    # Converte as emissões totais para toneladas de CO2 equivalente
    total_emissions = total_emissions / 1000 * farm_instance.Gwp[0]

    return total_emissions

# Exemplo de utilização:
onto = get_ontology("/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/ontologia_populada_sync_reasoner_pellet.owl").load()

# Suponha que você tenha uma instância específica da fazenda na ontologia
farm_instance = onto.RuralProperty

result = calculate_baseline_emissions_from_ontology(onto, farm_instance)
print(f"Emissões totais na situação de referência: {result:.2f} toneladas de CO2 equivalente")
