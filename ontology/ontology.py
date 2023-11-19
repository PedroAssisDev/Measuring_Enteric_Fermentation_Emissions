import csv

from owlready2 import *
from datetime import datetime

def generateOntology(run_reasoner=False, save=True, run_sensor=False):
    onto_path.append("/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/ontology")
    onto = get_ontology("http://www.semanticweb.org/owl/owlapi/mensuring_ontology#")
    with onto:
            # Definir classes
        class Cattle(Thing):
            pass
        
        class DairyCattle(Cattle):
            pass
        
        class OtherCattle(Cattle):
            pass
        
        class RuralProperty(Thing):
            pass
        
        class MeasurementData(Thing):
            pass
        
        class BaseLineEmissions(Thing):
            pass

    # Definir ObjectProperties
        class HasMeasurementData(ObjectProperty):
            domain = [DairyCattle, OtherCattle]
            range = [MeasurementData]
    
        class BelongsToProperty(ObjectProperty, FunctionalProperty,  SymmetricProperty):
            domain = [DairyCattle, OtherCattle]
            range = [RuralProperty]
        
        class HasCattleGroup(ObjectProperty, FunctionalProperty):
            inverse_property = BelongsToProperty
            domain = [RuralProperty]
            range = [DairyCattle, OtherCattle]
        
        class HasTotalEmissions(ObjectProperty, FunctionalProperty):
            domain = [BaseLineEmissions]
            range = [RuralProperty]
        
        class HasGroupEmissions(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [DairyCattle, OtherCattle]
        
        class HasAnimalQuantity(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [DairyCattle, OtherCattle]
        
        class HasMilkProduction(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [DairyCattle]
        
        class HasBaseLineEmissions(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [BaseLineEmissions]
        
        ############################# 
        class HasCattleId(ObjectProperty, FunctionalProperty):
            domain = [Cattle, MeasurementData]
            range = [str]

    # Definir DataProperties
        class cattleName(DataProperty):
            domain = [Cattle]
            range = [str]
        class cattleId(DataProperty):
            domain = [Cattle]
            range = [str]
        
        class peso(DataProperty):
            domain = [Cattle]
            range = [float]
               
        class producao(DataProperty):
            domain = [DairyCattle]
            range = [float]   
        
        class dataMedicao(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [datetime]
        
        class fatorEmissao(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        
        
        class TotalEmissions(DataProperty):
            domain = [RuralProperty]
            range = [float]
        
        class AnimalQuantity(DataProperty):
            domain = [RuralProperty]
            range = [int]
        
        class MilkProduction(DataProperty):
            domain = [RuralProperty]
            range = [float]
        
        class Gwp(DataProperty):
            domain = [RuralProperty]
            range = [float]
        
        class PropertyName(DataProperty):
            domain = [RuralProperty]
            range = [str]
        
        class measurementDate(DataProperty):
            domain = [MeasurementData]
            range = [datetime]
        
        class daysOnFarm(DataProperty):
            domain = [MeasurementData]
            range = [int]
        
        class entericEmissionFactor(DataProperty):
            domain = [MeasurementData]
            range = [float]
        # Adicione a regra SWRL
        rule = Imp()
        rule.set_as_rule(
            'DairyCattle(?c) ^ MeasurementData(?m) ^ hasMeasurementData(?c, ?m) ^ hasCattleId(?c, ?id) ^ hasCattleId(?m, ?id) -> differentFrom(?c, ?m)'
        )
        rule_individual = Rule()
        rule_individual.is_a.append(rule)
        # Salvar a ontologia
        if save:
            onto.save(file="ontologia.owl", format="rdfxml")

    
def popula_ontologia():
    fileName = r"ontologia.owl"
    
    if os.path.isfile(fileName):
        onto = get_ontology('ontologia.owl')
        onto.load()
    else:
        generateOntology(True, True, True)
        onto = get_ontology('ontologia.owl')
        onto.load()

    cow_instances = {}  # Dictionary to store unique cow instances based on 'Brinco'

    with onto:
        with open('/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/data'
                  '/Fazenda_Abc_dados_vacas.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            nome_propriedade_rural = "NomeDaSuaFazenda"
            propriedade_rural = onto.RuralProperty()
            propriedade_rural.PropertyName.append(nome_propriedade_rural)
            propriedade_rural.Gwp.append(28)
            for row in reader:
                cow_id = row['Brinco']
                
                # Criar uma nova instância de DairyCattle apenas se ainda não existir para essa vaca
                if cow_id not in cow_instances:
                    cow_instance = onto.DairyCattle(cattleId=[cow_id], cattleName=[str("Cattle" + row['Brinco'])])
                    cow_instances[cow_id] = cow_instance
                    cow_instance.BelongsToProperty = propriedade_rural
                else:
                    cow_instance = cow_instances[cow_id]

                # Criar uma instância de MeasurementData para cada linha de dados
                measurement_data = onto.MeasurementData()
                measurement_data.measurementDate.append(datetime.strptime(row['Date'], "%Y-%m-%d"))
                measurement_data.cattleId.append(str(row['Brinco']))
                measurement_data.peso.append(float(row['Peso']))
                measurement_data.producao.append(float(row['Leite']))
                measurement_data.fatorEmissao.append(103)

                # Conectar a instância de MeasurementData à instância de DairyCattle usando a propriedade HasMeasurementData
                cow_instances[str(row['Brinco'])].HasMeasurementData.append(measurement_data)

                # Conectar a instância de DairyCattle à propriedade rural usando a propriedade BelongsToProperty

    # Save the populated ontology
    onto.save(file="ontologia_populada.owl", format="rdfxml")
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)  # Pellet

    # Save the updated ontology
    onto.save(file="ontologia_populada_sync_reasoner_pellet.owl", format="rdfxml")

# Call the function to populate the ontology
popula_ontologia()