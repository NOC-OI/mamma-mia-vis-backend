from fastapi import FastAPI
from factory import ZarrTilerFactory
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Zarr Reader API", description="Zarr Reader API of MAMMA MIA visualisation")


origins = [
    "http://localhost:8080",  # Allow your Angular app's origin
    # Add other origins if needed (e.g., for production)
    # "*" for all origins (less secure - use with caution)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # If you need to send cookies or authorization headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Zarr API endpoints
zarr_factory = ZarrTilerFactory()
app.include_router(zarr_factory.router, tags=["Zarr API"])

