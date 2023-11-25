import csv
import pandas as pd
from owlready2 import *

from datetime import datetime

# Obtendo o caminho do diretório pai do arquivo .py
current_directory = os.path.dirname(os.path.abspath(__file__))
# Construindo caminhos para os diretórios e arquivos
base_directory = os.path.dirname(current_directory)
ontology_directory = os.path.join(base_directory, "ontology")
data_directory = os.path.join(base_directory, "data")
# Lista de caminhos dos arquivos/diretórios
file_ontology_1 = os.path.join(ontology_directory, "ontologia.owl")
file_ontology_2 = os.path.join(ontology_directory, "ontologia_final_populada.owl")
file_ontology_3 = os.path.join(ontology_directory, "ontologia_populada_sync_reasoner_pellet.owl")
file_data = os.path.join(data_directory, "pesoXleite_parsed.csv")


def generateOntology(save=True):
    onto_path.append(file_ontology_1)
    onto = get_ontology("http://www.semanticweb.org/owl/owlapi/mensuring_ontology#")
    with onto:
            # Definir classes
        class Cattle(Thing):
            pass
        
        class DairyCattle(Cattle):
            pass
        
        class OtherCattle(Cattle):
            pass
        
        #AllDisjoint([DairyCattle, OtherCattle])
        
        class RuralProperty(Thing):
            pass
        
        class MeasurementData(Thing):
            pass
        
        class BaseLineEmissions(Thing):
            pass
        class BaseLineEmissionsTier1(BaseLineEmissions):
            pass
        class BaseLineEmissionsTier2(BaseLineEmissions):
            pass

        
        # Definir DataProperties
        class cattleName(DataProperty):
            domain = [Cattle]
            range = [str]
        class cattleId(DataProperty):
            domain = [Cattle]
            range = [str]
        
        class weight(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
               
        class milkProduction(DataProperty):
            domain = [DairyCattle, MeasurementData]
            range = [float]   
        
        class measurementDate(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [datetime]
        
        class emissionFactor(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class energyDensity(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class dryMatterIntake(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class monthsOnFarm(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [int]        
        
        class animalQuantity(DataProperty):
            domain = [RuralProperty]
            range = [int]
        
        class totalMilkProduction(DataProperty):
            domain = [RuralProperty]
            range = [float]
        
        class gwp(DataProperty):
            domain = [Cattle, RuralProperty]
            range = [float]
        
        class propertyName(DataProperty):
            domain = [RuralProperty]
            range = [str]      
        
        class totalEmissionsTier1(DataProperty):
            domain = [RuralProperty, BaseLineEmissions]
            range = [float]
        class totalEmissionsTier2(DataProperty):
            domain = [RuralProperty, BaseLineEmissions]
            range = [float]
            
        class grossEnergyIntake(DataProperty):
            domain = [BaseLineEmissionsTier2]
            range = [float]
            
        class totalEntericEmissionFactorTier1(DataProperty):
            domain = [BaseLineEmissionsTier1]
            range = [float]
            
        class totalEntericEmissionFactorTier2(DataProperty):
            domain = [BaseLineEmissionsTier2]
            range = [float]
    
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
        
        class HasBaseLineEmissions(ObjectProperty, FunctionalProperty, SymmetricProperty):
            domain = [RuralProperty]
            range = [BaseLineEmissions]
        
        ############################# 
        class HasCattleId(ObjectProperty, FunctionalProperty):
            domain = [Cattle, MeasurementData]
            range = [str]        
        # Adicione a regra SWRL
        rule = Imp()
        rule.set_as_rule('Cattle(?c1) ^ Cattle(?c2) ^ HasCattleId(?c1, ?id1) ^ HasCattleId(?c2, ?id2) ^ differentFrom(?c1, ?c2) -> differentFrom(?id1, ?id2) ^ differentFrom(?c1, ?id2) ^ differentFrom(?c2, ?id1)')
        print("SWRL Rule:", rule)
        # Salvar a ontologia
        if save:
            onto.save(file=file_ontology_1, format="rdfxml")

    
def populaOntologia():
    fileName = r"ontologia_final.owl"
    
    if os.path.isfile(fileName):
        onto = get_ontology(file_ontology_1)
        onto.load()
    else:
        generateOntology(True)
        onto = get_ontology(file_ontology_1)
        onto.load()

    cow_instances = {}  # Dictionary to store unique cow instances based on 'Brinco'

    with onto:
        with open(file_data, newline='') as csvfile:
            basilene = onto.BaseLineEmissions()
            propriedade_rural = onto.RuralProperty()
            propriedade_rural.HasBaseLineEmissions = basilene
            nome_propriedade_rural = "RuralProperty1"
            propriedade_rural.propertyName.append(nome_propriedade_rural)
            propriedade_rural.gwp.append(28)
            df = pd.read_csv(file_data)

            for _, row in df.iterrows():
                cow_id = row['Brinco']

                # Create a new instance of DairyCattle if it doesn't exist for this cow
                if cow_id not in cow_instances:
                    cow_instance = onto.DairyCattle(cattleId=[str(cow_id)])
                    cow_instance.cattleName.append(f"Cattle{str(row['Brinco'])}")
                    cow_instance.gwp.append(28)
                    cow_instance.emissionFactor.append(103)
                    cow_instance.monthsOnFarm.append(int(df[df['Brinco'] == cow_id]['Date'].count()))
                    cow_instances[cow_id] = cow_instance
                    cow_instance.BelongsToProperty = propriedade_rural
                else:
                    cow_instance = cow_instances[cow_id]

                # Create an instance of MeasurementData for each data row
                measurement_data = onto.MeasurementData()
                measurement_data.measurementDate.append(datetime.strptime(row['Date'], "%Y-%m-%d"))
                measurement_data.cattleId.append(str(row['Brinco']))
                measurement_data.weight.append(float(row['Peso']))
                measurement_data.milkProduction.append(float(row['Leite']))
                measurement_data.emissionFactor.append(103)

                # Connect the MeasurementData instance to the DairyCattle instance
                cow_instance.HasMeasurementData.append(measurement_data)


    # Save the populated ontology
    onto.save(file=file_ontology_2, format="rdfxml")
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)  # Pellet
    
    # Save the updated ontology
    onto.save(file=file_ontology_3, format="rdfxml")
    
def getOntologia():
    populaOntologia()
    return get_ontology('ontology/ontologia_final.owl')

    
# Call the function to populate the ontology
populaOntologia()