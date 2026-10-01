# CarbonSECO for Livestock

Service suite for quantifying, monitoring, and supporting decisions about methane emissions from livestock enteric fermentation, with focus on Brazilian dairy farms.

This repository is the software artifact associated with the ICEIS 2024 paper:

> Silva, P.; Braga, R.; David, J.; Neto, V.; Arbex, W.; Stroele, V. CarbonSECO for Livestock: A Service Suite to Help in Carbon Emission Decisions. 26th International Conference on Enterprise Information Systems; pp. 89–99.

**Paper links**
- PDF (SciTePress): https://www.scitepress.org/Papers/2024/127343/127343.pdf
- SciLit: https://www.scilit.com/publications/d2d9362e06848cc78697a7ff32c04173
- DOI: [10.5220/0012734300003690](https://doi.org/10.5220/0012734300003690)

## Objective

Provide reproducible services that:

- ingest Smart Farm milking data;
- populate and query the **EntericMeasureOnto** ontology (OWL + SWRL + Pellet);
- compute IPCC/VCS-style **Tier 1** and **Tier 2** enteric emission baselines;
- project alternative scenarios with a linear regression model;
- expose results through FastAPI and a Streamlit dashboard.

## Relation to the scientific article

| Paper component | Implementation |
|---|---|
| Smart Farm dataset | `data/raw/pesoXleite.csv` |
| Data preparation | `carbonseco_livestock.preprocessing` |
| EntericMeasureOnto + SWRL S1–S6 | `carbonseco_livestock.ontology` + `ontology_assets/` |
| Equations (1)–(4) | `carbonseco_livestock.emissions` |
| Decision-support ML | `carbonseco_livestock.ml` + `models/linear_regression_model.pkl` |
| Dashboard / figures | `carbonseco_livestock.visualization` |
| Feasibility projection (598.48 tCO₂e) | `scripts/reproduce_feasibility_projection.py` |

## Architecture

```text
raw farm CSV
  -> preprocessing
  -> processed CSV
  -> ontology population (+ Pellet)
  -> SPARQL / monthly aggregates
  -> Tier1/Tier2 calculations
  -> API + dashboard

synthetic CSV
  -> linear regression training
  -> model pickle
  -> scenario projections
```

Details: [`docs/architecture.md`](docs/architecture.md).

## Requirements

- Python 3.10–3.13 (on Windows + Python 3.13, NumPy >= 2.1 is required)
- Java runtime on `PATH` (required only when running Pellet via owlready2)
- Dependencies declared in [`pyproject.toml`](pyproject.toml)

## Installation

```bash
git clone https://github.com/PedroAssisDev/Measuring_Enteric_Fermentation_Emissions.git
cd Measuring_Enteric_Fermentation_Emissions
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -e ".[dev]"
```

Alternatively:

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Configuration

- Scientific parameters: [`configs/scientific_params.yaml`](configs/scientific_params.yaml)
  - GWP methane = 28
  - Tier 1 EF = 78 kg CH₄ head⁻¹ d⁻¹
  - Tier 2 Ym-like factor = 6.5
  - Methane energy content EC = 55.65 MJ kg⁻¹
- Optional environment variables: see [`.env.example`](.env.example)
- Paths are resolved relative to the repository root (`pathlib`); override with `CARBONSECO_ROOT` if needed.

## Data layout

```text
data/
  raw/pesoXleite.csv                 # Smart Farm observations (2021)
  processed/pesoXleite_parsed.csv    # aggregated + diet features
  processed/sintetico.csv            # synthetic ML training set
ontology_assets/                     # TBox / populated / reasoned OWL
models/linear_regression_model.pkl   # trained projection model
results/                             # runtime exports
```

The committed `pesoXleite_parsed.csv`, OWL files, and model pickle are the reference artifacts used to reproduce the published feasibility-study results.

## Execution

### Parse farm data

```bash
python scripts/parse_farm_data.py
# or: carbonseco-parse
```

### Build / populate ontology

```bash
python scripts/build_ontology.py
# TBox only:
python scripts/build_ontology.py --tbox-only
```

### Generate synthetic data and train model

```bash
python scripts/generate_synthetic_data.py
python scripts/train_emission_model.py
```

### API

```bash
python scripts/run_api.py
# http://127.0.0.1:8000
# Endpoints:
#   GET /prod/Predictions/?days=335&average_DMI=21&energy_density_of_feed=18&average_number_of_heads=200
#   GET /prod/period/?start_month=1&start_year=2021&end_month=12&end_year=2021
#   GET /prod/totalYear/?aux=0
```

### Dashboard

```bash
python scripts/run_dashboard.py
# or: streamlit run src/carbonseco_livestock/visualization/dashboard.py
```

## Reproducing the paper projection

```bash
python scripts/reproduce_feasibility_projection.py
```

Expected output (rounded): **598.48 tCO₂e** for inputs days=335, DMI=21, energy density=18, heads=200.

## Generating results

- Monthly emission tables are exported by the dashboard to `results/monthly_emissions_export.csv`.
- API JSON responses expose yearly/period aggregates and projections.
- Ontology reasoning writes/reads OWL files under `ontology_assets/`.

## Running tests

```bash
pytest
```

Test layers:

- `tests/unit` — formulas, preprocessing, synthetic generation
- `tests/integration` — OWL load + monthly dataframe
- `tests/regression` — paper projection and artifact SHA-256 hashes

## Main technologies

Python, pandas, NumPy, scikit-learn, owlready2, Pellet, rdflib, FastAPI, Uvicorn, Streamlit, Plotly, PyYAML, pytest, Ruff.

## Directory structure

```text
configs/
data/{raw,processed}/
docs/
models/
ontology_assets/
scripts/
src/carbonseco_livestock/
tests/{unit,integration,regression,fixtures}/
results/
parser/, ML/, ontology/, src/   # thin compatibility shims
```

## Citation

Silva, P.; Braga, R.; David, J.; Neto, V.; Arbex, W.; Stroele, V. CarbonSECO for Livestock: A Service Suite to Help in Carbon Emission Decisions. 26th International Conference on Enterprise Information Systems; pp. 89–99.

- PDF: https://www.scitepress.org/Papers/2024/127343/127343.pdf
- SciLit: https://www.scilit.com/publications/d2d9362e06848cc78697a7ff32c04173
- DOI: https://doi.org/10.5220/0012734300003690

```bibtex
@inproceedings{silva2024carbonseco,
  author    = {Silva, Pedro Henrique Assis and Braga, Regina and David, Jos{\'e} Maria
               and Neto, Valdemar Vicente Graciano and Arbex, Wagner and Stroele, Victor},
  title     = {{CarbonSECO for Livestock: A Service Suite to Help in Carbon Emission Decisions}},
  booktitle = {Proceedings of the 26th International Conference on Enterprise Information Systems - Volume 2: ICEIS},
  year      = {2024},
  pages     = {89--99},
  publisher = {SciTePress},
  doi       = {10.5220/0012734300003690},
  url       = {https://www.scitepress.org/Papers/2024/127343/127343.pdf}
}
```

## License

The associated paper is published under **CC BY-NC-ND 4.0**. If you redistribute this software artifact, preserve attribution and check institutional/publisher constraints for the paper PDF and farm data.
