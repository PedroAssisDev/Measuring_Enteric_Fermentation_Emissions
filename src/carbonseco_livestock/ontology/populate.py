"""Populate EntericMeasureOnto ABox from processed farm CSV and run Pellet."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from owlready2 import AllDifferent, get_ontology, sync_reasoner_pellet

from carbonseco_livestock.config import get_project_paths, load_scientific_params
from carbonseco_livestock.ontology.build import generate_ontology
from carbonseco_livestock.utils import get_logger

logger = get_logger(__name__)


def populate_ontology(
    *,
    data_path: str | Path | None = None,
    tbox_path: str | Path | None = None,
    populated_path: str | Path | None = None,
    reasoned_path: str | Path | None = None,
    run_reasoner: bool = True,
):
    """Instantiate DairyCattle/MeasurementData individuals and optionally reason."""
    paths = get_project_paths()
    params = load_scientific_params()

    file_data = Path(data_path) if data_path is not None else paths.processed_farm_csv
    file_ontology_1 = Path(tbox_path) if tbox_path is not None else paths.ontology_tbox
    file_ontology_2 = (
        Path(populated_path) if populated_path is not None else paths.ontology_populated
    )
    file_ontology_3 = (
        Path(reasoned_path) if reasoned_path is not None else paths.ontology_reasoned
    )

    if file_ontology_1.is_file():
        onto = get_ontology(str(file_ontology_1))
        onto.load()
    else:
        generate_ontology(True, output_path=file_ontology_1)
        onto = get_ontology(str(file_ontology_1))
        onto.load()

    if not file_data.exists():
        raise FileNotFoundError(f"Processed farm CSV not found: {file_data}")

    cow_instances: dict[object, object] = {}
    cow_instances_list: list[object] = []

    with onto:
        df = pd.read_csv(file_data)
        gwp = params.gwp_methane
        emission_factor_tier_1 = params.emission_factor_tier1_kg_ch4_per_head_per_day
        emission_factor_tier_2 = params.emission_factor_tier2_ym_percent
        check_aux = all(col in df.columns for col in ["energyDensity", "dryMatterIntake"])
        baseline_tier1 = onto.BaseLineEmissionsTier1()
        baseline_tier2 = onto.BaseLineEmissionsTier2()
        rural_property = onto.RuralProperty()
        rural_property.HasBaseLineEmissions = [baseline_tier1, baseline_tier2]

        rural_property.propertyName.append("RuralProperty1")
        rural_property.gwp.append(gwp)

        for _, row in df.iterrows():
            cow_id = row["Brinco"]

            if cow_id not in cow_instances:
                cow_instance = onto.DairyCattle(cattleId=[str(cow_id)])
                cow_instance.cattleName.append("Cattle" + str(row["Brinco"]))
                cow_instance.gwp.append(gwp)
                cow_instance.emissionFactorTier1.append(emission_factor_tier_1)
                months_on_farm = float(df[df["Brinco"] == cow_id]["Date"].count())
                cow_instance.monthsOnFarm.append(months_on_farm)
                cow_instance.daysOnFarm.append(
                    months_on_farm * params.days_per_month_approximation
                )
                cow_instances[cow_id] = cow_instance
                cow_instances_list.append(cow_instance)
                cow_instance.BelongsToProperty.append(rural_property)
                if check_aux:
                    cow_instance.energyDensity.append(float(row["energyDensity"]))
                    cow_instance.dryMatterIntake.append(float(row["dryMatterIntake"]))
                    cow_instance.emissionFactorTier2.append(emission_factor_tier_2)
                else:
                    cow_instance.energyDensity.append(0.0)
                    cow_instance.dryMatterIntake.append(0.0)
                    cow_instance.emissionFactorTier2.append(0.0)
            else:
                cow_instance = cow_instances[cow_id]

            measurement_data = onto.MeasurementData()
            measurement_data.measurementDate.append(
                datetime.strptime(str(row["Date"]), "%Y-%m-%d")
            )
            measurement_data.cattleId.append(str(row["Brinco"]))
            measurement_data.weight.append(float(row["Peso"]))
            measurement_data.milkProduction.append(float(row["Leite"]))
            measurement_data.emissionFactorTier1.append(emission_factor_tier_1)
            if check_aux:
                measurement_data.energyDensity.append(float(row["energyDensity"]))
                measurement_data.dryMatterIntake.append(float(row["dryMatterIntake"]))
                measurement_data.emissionFactorTier2.append(emission_factor_tier_2)
            else:
                measurement_data.energyDensity.append(0.0)
                measurement_data.dryMatterIntake.append(0.0)
                measurement_data.emissionFactorTier2.append(0.0)

            cow_instance.HasMeasurementData.append(measurement_data)

        AllDifferent(cow_instances_list)
        rural_property.animalQuantity.append(len(cow_instances_list))
        rural_property.totalMilkProduction.append(float(df["Leite"].sum()))

    file_ontology_2.parent.mkdir(parents=True, exist_ok=True)
    onto.save(file=str(file_ontology_2), format="rdfxml")
    logger.info("Saved populated ontology to %s", file_ontology_2)

    if run_reasoner:
        try:
            sync_reasoner_pellet(
                infer_property_values=True,
                infer_data_property_values=True,
            )
        except Exception as exc:  # Pellet/Java failures are environment-specific
            logger.error("Reasoner inference failed: %s", exc)
        onto.save(file=str(file_ontology_3), format="rdfxml")
        logger.info("Saved reasoned ontology to %s", file_ontology_3)

    return onto


def get_ontology_reasoned(reasoned_path: str | Path | None = None):
    """Populate (if needed) and return the reasoned ontology handle."""
    paths = get_project_paths()
    target = Path(reasoned_path) if reasoned_path is not None else paths.ontology_reasoned
    if not target.exists():
        populate_ontology(reasoned_path=target)
    return get_ontology(str(target))
