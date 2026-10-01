"""FastAPI application exposing CarbonSECO livestock services."""

from __future__ import annotations

from fastapi import FastAPI

from carbonseco_livestock.api.services import EmissionServices


def create_app(*, load_on_startup: bool = True) -> FastAPI:
    app = FastAPI(
        title="CarbonSECO for Livestock",
        description="Services for enteric fermentation emission quantification and projection",
        version="1.0.0",
    )
    services = EmissionServices()

    @app.on_event("startup")
    def _startup() -> None:
        if load_on_startup:
            services.load(sync_pellet=True)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"Hello": "World"}

    @app.get("/prod/totalYear/")
    def total_year(aux: int = 0) -> dict[str, list[float]]:
        # `aux` retained for backwards-compatible query signature.
        _ = aux
        return services.total_year_aggregates()

    @app.get("/prod/Predictions/")
    def predictions(
        days: float,
        average_DMI: float,
        energy_density_of_feed: float,
        average_number_of_heads: float,
    ) -> dict[str, list[float]]:
        return {
            "Predictions scenario": services.predict(
                days,
                average_DMI,
                energy_density_of_feed,
                average_number_of_heads,
            )
        }

    @app.get("/prod/period/")
    def period(
        start_month: int,
        start_year: int,
        end_month: int,
        end_year: int,
    ) -> dict[str, list[float]]:
        return services.period_aggregates(start_month, start_year, end_month, end_year)

    app.state.services = services
    return app


app = create_app(load_on_startup=True)
