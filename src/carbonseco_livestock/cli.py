"""Console entry points for CarbonSECO livestock pipelines."""

from __future__ import annotations

import argparse
import sys

import uvicorn


def parse_farm_data_cli(argv: list[str] | None = None) -> None:
    from carbonseco_livestock.preprocessing import parse_farm_file

    parser = argparse.ArgumentParser(description="Parse Smart Farm milking CSV")
    parser.add_argument("--input", default=None, help="Raw CSV path")
    parser.add_argument("--output", default=None, help="Processed CSV path")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for ED/DMI placeholders (omit to keep unseeded behavior)",
    )
    args = parser.parse_args(argv)
    parse_farm_file(args.input, output_path=args.output, random_seed=args.seed)


def build_ontology_cli(argv: list[str] | None = None) -> None:
    from carbonseco_livestock.ontology import generate_ontology, populate_ontology

    parser = argparse.ArgumentParser(description="Build/populate EntericMeasureOnto")
    parser.add_argument(
        "--tbox-only",
        action="store_true",
        help="Only generate TBox + SWRL (no ABox population)",
    )
    parser.add_argument(
        "--skip-reasoner",
        action="store_true",
        help="Populate ABox without Pellet reasoning",
    )
    args = parser.parse_args(argv)
    if args.tbox_only:
        generate_ontology(save=True)
    else:
        populate_ontology(run_reasoner=not args.skip_reasoner)


def generate_synthetic_cli(argv: list[str] | None = None) -> None:
    from carbonseco_livestock.ml import generate_synthetic_data

    parser = argparse.ArgumentParser(description="Generate synthetic ML training data")
    parser.add_argument("--samples", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    generate_synthetic_data(args.samples, seed=args.seed, output_path=args.output)


def train_model_cli(argv: list[str] | None = None) -> None:
    from carbonseco_livestock.ml import train_linear_regression_model

    parser = argparse.ArgumentParser(description="Train linear regression emission model")
    parser.add_argument("--data", default=None)
    parser.add_argument("--model", default=None)
    args = parser.parse_args(argv)
    train_linear_regression_model(data_path=args.data, model_path=args.model)


def run_api_cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run CarbonSECO FastAPI service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    uvicorn.run(
        "carbonseco_livestock.api.app:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


def run_dashboard_cli(argv: list[str] | None = None) -> None:
    import subprocess

    parser = argparse.ArgumentParser(description="Run CarbonSECO Streamlit dashboard")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args(argv)
    import carbonseco_livestock.visualization.dashboard as dash_mod

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dash_mod.__file__),
        "--server.port",
        str(args.port),
    ]
    raise SystemExit(subprocess.call(cmd))
