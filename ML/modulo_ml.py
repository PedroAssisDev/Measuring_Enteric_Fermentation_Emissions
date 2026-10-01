"""Compatibility shim — prefer carbonseco_livestock.ml.train."""

from __future__ import annotations

from carbonseco_livestock.ml import train_linear_regression_model

if __name__ == "__main__":
    train_linear_regression_model()
