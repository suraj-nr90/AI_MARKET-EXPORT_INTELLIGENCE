from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import research, events, reports, sectors, companies

from contextlib import asynccontextmanager
from services.db import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()

app = FastAPI(
    title="Export Market Intelligence API",
    description="Backend API for regional thermal packaging export analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS so Next.js frontend can make API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(research.router)
app.include_router(events.router)
app.include_router(reports.router)
app.include_router(sectors.router)
app.include_router(companies.router)
