# Refactoring Report — CarbonSECO for Livestock

## 1. Executive summary

The repository was reorganized into an installable scientific Python package (`carbonseco_livestock`) with centralized emission formulas, portable paths, explicit scientific parameters, CLI scripts, regression tests (including the paper projection **598.48 tCO₂e**), and documentation suitable as a publication artifact. Scientific algorithms, SWRL rules, and committed baselines were preserved.

## 2. Previous architecture

Loose scripts under `parser/`, `ontology/`, `ML/`, and `src/` with manual execution order, duplicated Tier1/Tier2 logic between FastAPI and Streamlit, incomplete `requirements.txt`, absolute Linux path side-effects in the parser, and no automated tests.

## 3. New architecture

Package layout under `src/carbonseco_livestock/` separating:

- configuration (`config/`, `configs/scientific_params.yaml`)
- scientific calculations (`emissions/`)
- preprocessing, ontology, ML
- thin API/dashboard adapters
- scripts for reproduction

Committed artifacts moved to `data/raw`, `data/processed`, `ontology_assets/`, and `models/`.

## 4. Main problems found

- Non-portable absolute path executed by the parser
- Incomplete dependency declaration
- Duplicated scientific calculators
- Missing reproducibility docs/tests

## 5. Changes by module

| Area | Change |
|---|---|
| `emissions/` | Single source for Tier1/Tier2/BE formulas |
| `preprocessing/` | Farm parse without import side-effects; optional seed |
| `ontology/` | TBox/SWRL/populate/query modules |
| `ml/` | Synthetic generation, training, prediction APIs |
| `api/` | FastAPI factory + service layer |
| `visualization/` | Streamlit UI using shared calculators/queries |
| `tests/` | Unit, integration, scientific regression |
| Compatibility shims | Old entry points delegate to the package |

## 6. Removed / relocated code

- Absolute-path auto-execution removed from parser import path
- Large OWL/CSV/model artifacts relocated (not deleted)
- Dashboard cwd `test.csv` side-effect replaced by `results/monthly_emissions_export.csv`
- Orphan `__pycache__` ignored via `.gitignore` (not treated as source)

No scientifically meaningful module was deleted without a shim or replacement.

## 7. Dependencies

- Added/declared: numpy, scikit-learn, joblib, rdflib, streamlit, plotly, PyYAML, pytest, ruff
- Kept: pandas, fastapi, uvicorn, owlready2
- Centralized in `pyproject.toml`; `requirements.txt` updated as a mirror

## 8. Tests

- Unit: emission formulas, preprocessing, synthetic seeding
- Integration: OWL load + monthly dataframe invariants
- Regression: paper projection ≈ 598.483996… and SHA-256 hashes of committed artifacts
- Validation run after refactoring: **20 passed** (`pytest`), projection script output `598.48` matching the paper

## 9. Reproducibility

1. `pip install -e ".[dev]"`
2. Use committed processed CSV / OWL / model for baseline results
3. `python scripts/reproduce_feasibility_projection.py`
4. `pytest`

Pellet/Java is required only for ontology re-reasoning.

## 10. Scientific compatibility

- Paper projection preserved against committed model.
- Artifact hashes frozen for raw/processed/synthetic/OWL/model files.
- Operational fix: `/prod/period/` date construction coerces Year/Month to strings.

## 11. Future improvements

- Optional CI workflow running `pytest` on push
- Replace FastAPI `on_event` with lifespan API when raising minimum FastAPI version
