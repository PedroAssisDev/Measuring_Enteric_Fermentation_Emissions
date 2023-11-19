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
        class HasMeasurementData(ObjectProperty, FunctionalProperty):
            domain = [DairyCattle, OtherCattle]
            range = [MeasurementData]
    
        class BelongsToProperty(ObjectProperty, FunctionalProperty, SymmetricProperty):
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
        # Salvar a ontologia
        if save:
            onto.save(file="ontologia_v2.owl", format="rdfxml")


def popula_ontologia():
    fileName = r"ontologia_v2.owl"
    # Exemplo de chamada da função
    if os.path.isfile(fileName):
        onto = get_ontology('ontologia_v2.owl')
        onto.load()
    else:
        generateOntology(True, True, True)
        onto = get_ontology('ontologia_v2.owl')
        onto.load()

    with onto:
        with open('/home/pedro_estudos/Documentos/GitHub/Measuring_Enteric_Fermentation_Emissions/data'
                  '/Fazenda_Abc_dados_vacas.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            nome_propriedade_rural = "NomeDaSuaFazenda"
            propriedade_rural = onto.RuralProperty
            propriedade_rural.PropertyName.append(nome_propriedade_rural)
            propriedade_rural.Gwp.append(28)
            for row in reader:
                # Criar instância da classe Cattle
                # Isso criará uma nova instância ou obterá uma existente com o mesmo nome
                vaca = onto.DairyCattle(BelongsToProperty= propriedade_rural)

                # Criar instância de MeasurementData para cada linha de dados
                measurement_data = onto.MeasurementData()
                measurement_data.measurementDate = (datetime.strptime(row['Date'], "%Y-%m-%d"))
                measurement_data.cattleId.append(str(row['Brinco']))
                measurement_data.peso.append(float(row['Peso']))
                measurement_data.producao.append(float(row['Leite']))
                measurement_data.fatorEmissao.append(103)

                # Conectar a instância de MeasurementData à instância de DairyCattle usando a propriedade HasMeasurementData
                vaca.HasMeasurementData.append(measurement_data)

    onto.save(file="ontologia_v2_populada.owl", format="rdfxml")

    # Executar o raciocinador
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)  # Pellet


    # Salvar a ontologia atualizada
    onto.save(file="ontologia_populada_sync_reasoner_pellet.owl", format="rdfxml")
popula_ontologia()