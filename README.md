# MAMMA MIA Visualization Backend

The [MAMMA MIA Visualization Backend](https://noc-oi.github.io/mamma-mia-vis-backend/) is a high-performance FastAPI service designed to serve oceanographic data. Data source comes from [MAMMA MIA toolbox](https://noc-mdp.github.io/MammaMia/) which simulates the payload (sensors) and trajectory of a platform (Autonomous Underwater Vehicle).

## Run backend API locally
To run backend API locally, run the following command:
```bash
% uvicorn main:app --reload --port 8040
```
Then, access interactive API docs at http://127.0.0.1:8040/docs

## Run backend API using Docker
You can also run the application using Docker.

### Using Docker Compose (Recommended)
This will build the image and start the container with the local `assets/` directory mounted.
```bash
docker-compose up
```

### Using Docker build
If you want to build and run the image manually:
```bash
docker build -t mamma-mia-vis-backend .
docker run -p 8040:8040 -v $(pwd)/assets:/app/assets mamma-mia-vis-backend
```

## Documentation with MkDocs
Project documentation is generated using **MkDocs** with the Material theme.

To serve documentation locally:
```bash
mkdocs serve
```
Then visit `http://127.0.0.1:8000`.

To build static documentation site:
```bash
mkdocs build
```
The documentation source files are located in the `docs/` folder (including [Getting Started with MAMMA MIA backend](docs/getting-started.md)).

