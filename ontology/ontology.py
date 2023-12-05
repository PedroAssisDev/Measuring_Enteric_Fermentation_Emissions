import csv
import pandas as pd
from owlready2 import *

from datetime import datetime

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ontology_directory = os.path.join(base_directory, "ontology")
data_directory = os.path.join(base_directory, "data")
file_ontology_1 = os.path.join(ontology_directory, "ontologia.owl")
file_ontology_2 = os.path.join(ontology_directory, "ontologia_final_populada.owl")
file_ontology_3 = os.path.join(ontology_directory, "ontologia_populada_sync_reasoner_pellet.owl")
file_data = os.path.join(data_directory, "pesoXleite_parsed.csv")


def generateOntology(save=True):
    onto_path.append(file_ontology_1)
    onto = get_ontology("http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#")
    with onto:
        class Cattle(Thing):
            pass
        
        class DairyCattle(Cattle):
            pass
        
        class OtherCattle(Cattle):
            pass
        AllDifferent([Cattle])
                
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
        AllDifferent([BaseLineEmissions])
        
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
        
        class emissionFactorTier1(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class emissionFactorTier2(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class energyDensity(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class dryMatterIntake(DataProperty):
            domain = [Cattle, MeasurementData]
            range = [float]
        class monthsOnFarm(DataProperty):
            domain = [Cattle]
            range = [float]  
        class daysOnFarm(DataProperty):
            domain = [Cattle]
            range = [float]      
        class totalIndividualEntericEmissionFactorTier1(DataProperty):
            domain = [Cattle]
            range = [float] 
        class totalIndividualEntericEmissionFactorTier2(DataProperty):
            domain = [Cattle]
            range = [float] 
        class animalQuantity(DataProperty):
            domain = [RuralProperty]
            range = [float]
        
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
            domain = [RuralProperty, BaseLineEmissions, Cattle]
            range = [float]
        class totalEmissionsTier2(DataProperty):
            domain = [RuralProperty, BaseLineEmissions, Cattle]
            range = [float]
            
        class grossEnergyIntake(DataProperty):
            domain = [Cattle]
            range = [float]
            
        class totalEntericEmissionFactorTier1(DataProperty):
            domain = [BaseLineEmissionsTier1]
            range = [float]
            
        class totalEntericEmissionFactorTier2(DataProperty):
            domain = [BaseLineEmissionsTier2]
            range = [float]
    
        class HasMeasurementData(ObjectProperty):
            domain = [Cattle]
            range = [MeasurementData]
    
        class BelongsToProperty(ObjectProperty, SymmetricProperty):
            domain = [Cattle]
            range = [RuralProperty]
        
        class HasCattleGroup(ObjectProperty):
            inverse_property = BelongsToProperty
            domain = [RuralProperty]
            range = [Cattle]
        
        class HasTotalEmissions(ObjectProperty, FunctionalProperty):
            domain = [BaseLineEmissions]
            range = [RuralProperty]
        
        class HasGroupEmissions(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [Cattle]
        
        class HasAnimalQuantity(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [Cattle]
        
        class HasMilkProduction(ObjectProperty, FunctionalProperty):
            domain = [RuralProperty]
            range = [DairyCattle]
        
        class HasBaseLineEmissions(ObjectProperty, SymmetricProperty):
            domain = [RuralProperty]
            range = [BaseLineEmissions]
        

        createRules()
        if save:
            onto.save(file=file_ontology_1, format="rdfxml")

def createRules():
    rule_milk_production_cattle = Imp()
    rule_milk_production_cattle.set_as_rule(
            'Cattle(?cattle) ^ milkProduction(?cattle, ?production) -> DairyCattle(?cattle)'
        )
    rule_enteric_emissionTier1_factor_per_individual = Imp()
    rule_enteric_emissionTier1_factor_per_individual.set_as_rule(
        'DairyCattle(?cattle) ^ '
        'emissionFactorTier1(?cattle, ?e) ^ '
        'daysOnFarm(?cattle, ?d) ^ '
        'multiply(?result, ?e, ?d) ^ '
        '-> totalIndividualEntericEmissionFactorTier1(?cattle, ?result)'
        )     
    rule_grossEnergyIntake_per_individual = Imp()
    rule_grossEnergyIntake_per_individual.set_as_rule(
        'DairyCattle(?cattle) ^ '
        'energyDensity(?cattle, ?e) ^ '
        'dryMatterIntake(?cattle, ?d) ^ '
        'multiply(?result, ?e, ?d) ^ '
        '-> grossEnergyIntake(?cattle, ?result)'
        ) 
    rule_sum_enteric_emission_and_multiply_gwp = Imp()
    rule_sum_enteric_emission_and_multiply_gwp.set_as_rule(
        'Cattle(?cattle) ^ '
        'grossEnergyIntake(?cattle, ?gei) ^ '
        'daysOnFarm(?cattle, ?d) ^ '
        'emissionFactorTier2(?cattle, ?ef) ^'
        'multiply(?result, ?gei, ?d, ?ef, 0.01) ^ '
        'divide(?finalResult, ?result, 55.65) ^ '
        '-> totalIndividualEntericEmissionFactorTier2(?cattle, ?finalResult)'
    )        

    print("SWRL Rule:", rule_milk_production_cattle)     

 
def populaOntologia():
       
    if os.path.isfile(file_ontology_1):
        onto = get_ontology(file_ontology_1)
        onto.load()
    else:
        generateOntology(True)
        onto = get_ontology(file_ontology_1)
        onto.load()

    cow_instances = {}  
    cow_instances_list = []

    with onto:
            df = pd.read_csv(file_data)
            checkAux = all(col in df.columns for col in ['energyDensity', 'dryMatterIntake'])
            basileneTier1 = onto.BaseLineEmissionsTier1()
            basileneTier2 = onto.BaseLineEmissionsTier2()
            propriedade_rural = onto.RuralProperty()
            propriedade_rural.HasBaseLineEmissions = [basileneTier1,basileneTier2]

            nome_propriedade_rural = "RuralProperty1"
            propriedade_rural.propertyName.append(nome_propriedade_rural)
            propriedade_rural.gwp.append(28.00)
            for _, row in df.iterrows():
                cow_id = row['Brinco']

                if cow_id not in cow_instances:
                    cow_instance = onto.DairyCattle(cattleId=[str(cow_id)])
                    cow_instance.cattleName.append("Cattle"+str(row['Brinco']))
                    cow_instance.gwp.append(28.00)
                    cow_instance.emissionFactorTier1.append(103.00)
                    cow_instance.monthsOnFarm.append(float(df[df['Brinco'] == cow_id]['Date'].count()))
                    cow_instance.daysOnFarm.append(float(df[df['Brinco'] == cow_id]['Date'].count())*30)
                    cow_instances[cow_id] = cow_instance
                    cow_instances_list.append(cow_instance)
                    cow_instance.BelongsToProperty.append(propriedade_rural)
                    if checkAux:
                        cow_instance.energyDensity.append(float(row['energyDensity']))
                        cow_instance.dryMatterIntake.append(float(row['dryMatterIntake']))
                        cow_instance.emissionFactorTier2.append(float(row['emissionFactorTier1']))
                    else:
                        cow_instance.energyDensity.append(0.0)
                        cow_instance.dryMatterIntake.append(0.0)
                        cow_instance.emissionFactorTier2.append(0.0)
                else:
                    cow_instance = cow_instances[cow_id]

                measurement_data = onto.MeasurementData()
                measurement_data.measurementDate.append(datetime.strptime(row['Date'], "%Y-%m-%d"))
                measurement_data.cattleId.append(str(row['Brinco']))
                measurement_data.weight.append(float(row['Peso']))
                measurement_data.milkProduction.append(float(row['Leite']))
                measurement_data.emissionFactorTier1.append(103)
                if checkAux:
                    measurement_data.energyDensity.append(float(row['energyDensity']))
                    measurement_data.dryMatterIntake.append(float(row['dryMatterIntake']))
                    measurement_data.emissionFactorTier2.append(float(row['emissionFactorTier1']))
                else:
                    measurement_data.energyDensity.append(0.0)
                    measurement_data.dryMatterIntake.append(0.0)
                    measurement_data.emissionFactorTier2.append(0.0)

                cow_instance.HasMeasurementData.append(measurement_data)
            AllDifferent(cow_instances_list)


    onto.save(file=file_ontology_2, format="rdfxml")
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)  # Pellet
    
    onto.save(file=file_ontology_3, format="rdfxml")
    
def getOntologia():
    populaOntologia()
    return get_ontology(file_ontology_3)

    
#populaOntologia()