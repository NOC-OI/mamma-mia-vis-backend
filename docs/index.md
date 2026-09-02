# MAMMA-MIA Visualization Backend

Welcome to the documentation for the **MAMMA-MIA Visualization Backend**.

## Overview

The MAMMA-MIA Visualization Backend is a high-performance FastAPI service designed to serve oceanographic data. Data source comes from [MAMMA MIA toolbox](https://noc-mdp.github.io/MammaMia/) which simulates the payload (sensors) and trajectory of a platform (Autonomous Underwater Vehicle). It exposes API endpoints to retrieve:

- Trajectory data from platforms such as Slocum Glider.
- Oceanographic sensor readings data from platforms like Autosub Long Range (ALR) and Slocum Glider, including:
    - Sea Water Practical Salinity
    - Sea Water Temperature
    - Mass Concentration of Chlorophyll in Sea Water
- Multi-dimensional Zarr dataset inspection, metadata and slice query capabilities.

## Architecture

The backend consists of:

- **FastAPI Application (`main.py`)**: Entry point defining app middleware (CORS) and dynamic route inclusion.
- **Zarr Tiler Factory (`factory.py`)**: Exposes structured API endpoints for retrieving variables, dimensions, spatial subsets, and data slices.
- **Zarr Reader Core (`reader.py`)**: Utilities for interfacing with Zarr stores, reading metadata, performing coordinate projections (`pyproj`), and slicing data.
- **Utilities (`utils/`)**: Helper functions for spatial conversions, timestamp parsing, and array processing.

## Documentation Structure

- [Getting Started with MAMMA-MIA backend](getting-started.md): Installation, running locally with Uvicorn, and Docker container deployment.
- [API Reference](api-reference.md): Detailed information on endpoints, request parameters, response schemas, and interactive Swagger/OpenAPI docs.
