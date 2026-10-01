"""Compatibility shim — prefer carbonseco_livestock.ml.synthetic."""

from __future__ import annotations

from carbonseco_livestock.ml import generate_synthetic_data

__all__ = ["generate_synthetic_data"]


if __name__ == "__main__":
    generate_synthetic_data()
