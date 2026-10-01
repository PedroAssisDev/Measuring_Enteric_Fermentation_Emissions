"""EntericMeasureOnto TBox and SWRL rule definitions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from owlready2 import (
    AllDifferent,
    DataProperty,
    FunctionalProperty,
    Imp,
    ObjectProperty,
    SymmetricProperty,
    Thing,
    get_ontology,
    onto_path,
)

from carbonseco_livestock.config import get_project_paths
from carbonseco_livestock.domain import ONTOLOGY_IRI
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)


def create_rules() -> None:
    """Register SWRL rules S1–S6 (paper Table 2 / historical code)."""
    rule_milk_production_cattle = Imp()
    rule_milk_production_cattle.set_as_rule(
        "Cattle(?cattle) ^ milkProduction(?cattle, ?production) -> DairyCattle(?cattle)"
    )

    rule_enteric_factor_emission_tier1_individual = Imp()
    rule_enteric_factor_emission_tier1_individual.set_as_rule(
        "DairyCattle(?cattle) ^ "
        "emissionFactorTier1(?cattle, ?e) ^ "
        "daysOnFarm(?cattle, ?d) ^ "
        "multiply(?result, ?e, ?d) ^ "
        "-> individualEntericEmissionFactorTier1(?cattle, ?result)"
    )

    rule_gross_energy_intake_per_individual = Imp()
    rule_gross_energy_intake_per_individual.set_as_rule(
        "DairyCattle(?cattle) ^ "
        "energyDensity(?cattle, ?e) ^ "
        "dryMatterIntake(?cattle, ?d) ^ "
        "multiply(?result, ?e, ?d) ^ "
        "-> grossEnergyIntake(?cattle, ?result)"
    )

    rule_enteric_factor_emission_tier2_individual = Imp()
    rule_enteric_factor_emission_tier2_individual.set_as_rule(
        "Cattle(?cattle) ^ "
        "grossEnergyIntake(?cattle, ?gei) ^ "
        "daysOnFarm(?cattle, ?d) ^ "
        "emissionFactorTier2(?cattle, ?ef) ^"
        "multiply(?result, ?gei, ?d, ?ef, 0.01) ^ "
        "divide(?finalResult, ?result, 55.65) ^ "
        "-> individualEntericEmissionFactorTier2(?cattle, ?finalResult)"
    )

    rule_enteric_emission_tier1_individual = Imp()
    rule_enteric_emission_tier1_individual.set_as_rule(
        "Cattle(?cattle) ^ "
        "individualEntericEmissionFactorTier1(?cattle, ?eeft1) ^ "
        "gwp(?cattle, ?gwp) ^ "
        "multiply(?result, ?eeft1, ?gwp, 0.001) ^ "
        "-> individualEntericEmissionTier1(?cattle, ?finalResult)"
    )

    rule_enteric_emission_tier2_individual = Imp()
    rule_enteric_emission_tier2_individual.set_as_rule(
        "Cattle(?cattle) ^ "
        "individualEntericEmissionFactorTier2(?cattle, ?eeft2) ^ "
        "gwp(?cattle, ?gwp) ^ "
        "multiply(?result, ?eeft2, ?gwp, 0.001) ^ "
        "-> individualEntericEmissionTier2(?cattle, ?finalResult)"
    )

    logger.info("SWRL Rule: %s", rule_milk_production_cattle)


def generate_ontology(
    save: bool = True,
    output_path: str | Path | None = None,
):
    """Create EntericMeasureOnto classes, properties, and SWRL rules."""
    paths = get_project_paths()
    tbox_path = Path(output_path) if output_path is not None else paths.ontology_tbox
    tbox_path.parent.mkdir(parents=True, exist_ok=True)

    onto_path.append(str(tbox_path.parent))
    onto = get_ontology(ONTOLOGY_IRI)
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

        class individualEntericEmissionFactorTier1(DataProperty):
            domain = [Cattle]
            range = [float]

        class individualEntericEmissionTier1(DataProperty):
            domain = [Cattle]
            range = [float]

        class individualEntericEmissionFactorTier2(DataProperty):
            domain = [Cattle]
            range = [float]

        class individualEntericEmissionTier2(DataProperty):
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

        create_rules()
        if save:
            onto.save(file=str(tbox_path), format="rdfxml")
            logger.info("Saved ontology TBox to %s", tbox_path)

    return onto
