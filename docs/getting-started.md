# Getting Started with MAMMA MIA backend

This guide will walk you through setting up and running the MAMMA MIA Visualization Backend locally or using Docker.

---

## Prerequisites

- **Python**: `3.10+` (Python 3.12 recommended)
- **Pip**: Latest version
- **Docker & Docker Compose**: (Optional, for containerized deployments)

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

You can containerize and run the application using Docker or Docker Compose.

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
