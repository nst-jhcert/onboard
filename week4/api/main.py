"""Week4 API server for CSP/CCSDS packet handling."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ccsds, csp

api = FastAPI(
    title="ONBOARD-WEEK4",
    docs_url="/docs",
    redoc_url="/redoc",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(csp.router, prefix="/csp", tags=["CSP"])
api.include_router(ccsds.router, prefix="/ccsds", tags=["CCSDS"])


@api.get("/")
def root():
    """Health check endpoint."""
    return {"status": "OK"}
