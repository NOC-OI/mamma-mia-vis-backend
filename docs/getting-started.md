# Getting Started with MAMMA MIA backend

This guide will walk you through setting up and running the MAMMA MIA Visualization Backend locally or using Docker.

---

## Prerequisites

### Dependencies
MAMMA MIA backend supports Python >=3.10 but Python 3.12 is recommended. Also, it's recommended to use latest version of pip. Alternatively, you can use Docker and Docker Compose for containerised deployments.

   ```
   fastapi>=0.115.8
   zarr>=3.0.2
   numpy>=2.2.2
   uvicorn>=0.34.0
   pandas>=3.0.0
   pyproj>=3.7.2
   mkdocs>=1.6.0
   mkdocs-material>=9.5.0
   ```
### Data

1. Create a folder called **data_inputs** under **assets** folder. Donwload data generated from MAMMA MIA toolbox at this link: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22306342.svg)](https://doi.org/10.5281/zenodo.22306342). Move data to this folder.
2. To use **trajectory data (CSV)** endpoint, you need to download a vertical grid file from this link: [EGM96 15' global vertical datum grid](https://github.com/OSGeo/proj-datumgrid/blob/master/egm96_15.gtx) and move it to PROJ data directory. For an installed PROJ this may be /usr/local/share/proj or /user/share/proj on unix style operating systems. For conda environments this may be /path/to/conda/env/share/proj. 

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/mamma-mia-vis-backend.git
   cd mamma-mia-vis-backend
   ```

2. **Set Up Virtual Environment (Recommended)**

      a. *Creating a Python virtual environment*
         ```bash
         python3 -m venv venv
         source venv/bin/activate
         ```
      b. *Alternatively, create a Conda environment*
         ```bash
         conda create --name mamma-mia-vis-backend
         conda activate mamma-mia-vis-backend
         ```

3. **Installing Backend Dependencies**

      a. *Install backend dependencies in the Python environment*
      ```bash
      pip install -r requirements.txt
      ```
      b. *Alternatively, install backend dependencies from requirements.txt in the Conda environment*
      ```bash
      conda install --file --yes requirements.txt
      ```

---

## Running Backend API Locally

To start the FastAPI server with auto-reload:

```bash
uvicorn main:app --reload --port 8040
```

Once running, the backend API is available at:

- **Base API URL**: `http://127.0.0.1:8040`
- **Interactive OpenAPI / Swagger Documentation**: [http://127.0.0.1:8040/docs](http://127.0.0.1:8040/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8040/redoc](http://127.0.0.1:8040/redoc)

---

## Running Backend API using Docker

You can containerise and run the application using Docker or Docker Compose.

### Using Docker Compose (Recommended)

Docker Compose builds the container image and automatically mounts the local `./assets/` directory for live data access:

```bash
docker-compose up
```

To run in detached (background) mode:
```bash
docker-compose up -d
```

### Using Docker Build

If you prefer building and running the container manually:

1. **Build the Image**
   ```bash
   docker build -t mamma-mia-vis-backend .
   ```

2. **Run the Container**
   ```bash
   docker run -p 8040:8040 -v $(pwd)/assets:/app/assets mamma-mia-vis-backend
   ```

---

## Generating & Viewing Documentation

Project documentation is powered by **MkDocs** with the Material theme.

- **Serve Documentation Locally** (with live reload):
  ```bash
  mkdocs serve
  ```
  Open `http://127.0.0.1:8000` in your web browser.

- **Build Static HTML Site**:
  ```bash
  mkdocs build
  ```
  The compiled site will be generated in the `site/` folder.
