from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import research, events, reports, sectors, companies

app = FastAPI(
    title="Export Market Intelligence API",
    description="Backend API for regional thermal packaging export analysis",
    version="1.0.0"
)

# Configure CORS so Next.js frontend can make API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
