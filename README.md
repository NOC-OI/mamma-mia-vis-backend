# MAMMA-MIA Visualization Backend

Backend API to get glider/ALR trajectory data and metrics readings like practical salinity, sea temperature and chlorophyll sensor data.

# API endpoints documentation
To access interactive API docs go to http://127.0.0.1:8040/docs

# Run backend API locally
To run backend API locally, run the following command:
```bash
% uvicorn main:app --reload --port 8040
```
# Run backend API using Docker
You can also run the application using Docker.

## Using Docker Compose (Recommended)
This will build the image and start the container with the local `assets/` directory mounted.
```bash
docker-compose up
```

## Using Docker build
If you want to build and run the image manually:
```bash
docker build -t mamma-mia-vis-backend .
docker run -p 8040:8040 -v $(pwd)/assets:/app/assets mamma-mia-vis-backend
```
