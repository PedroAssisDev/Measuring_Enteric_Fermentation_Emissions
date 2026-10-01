# Architecture — CarbonSECO for Livestock

## Overview

The repository implements the ICEIS 2024 CarbonSECO livestock services:

1. Farm data preprocessing
2. EntericMeasureOnto (OWL + SWRL + Pellet)
3. IPCC/VCS Tier 1 and Tier 2 emission calculations
4. Synthetic-data linear regression for projected scenarios
5. FastAPI services and Streamlit dashboard

## Package layout

```text
src/carbonseco_livestock/
  config/          # portable paths + scientific YAML params
  domain/          # ontology IRI / shared identifiers
  emissions/       # Tier1/Tier2/BE formulas (single source of truth)
  preprocessing/   # Smart Farm CSV parsing
  ontology/        # TBox, ABox population, SPARQL/dataframe queries
  ml/              # synthetic data, training, prediction
  api/             # FastAPI thin layer
  visualization/   # Streamlit thin layer
  utils/           # logging
```

## Scientific vs operational configuration

- Scientific constants live in `configs/scientific_params.yaml`.
- Operational paths are resolved from the repository root via `pathlib`.
- Committed OWL/model/CSV artifacts under `ontology_assets/`, `models/`, and `data/` are baselines for reproduction.

## Execution flow

```text
data/raw/pesoXleite.csv
  -> preprocessing.parse_farm_file
  -> data/processed/pesoXleite_parsed.csv
  -> ontology.populate_ontology (+ Pellet)
  -> ontology_assets/*.owl
  -> api / dashboard queries + emissions.calculations

data/processed/sintetico.csv
  -> ml.train_linear_regression_model
  -> models/linear_regression_model.pkl
  -> ml.predict_emissions
```
