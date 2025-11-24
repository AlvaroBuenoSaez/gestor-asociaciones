from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.v1 import users, socias, eventos, drive

app = FastAPI(
    title="Gestor Asociaciones API",
    description="Backend API using Hexagonal Architecture",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "architecture": "hexagonal"}

app.include_router(users.router, prefix="/api/v1")
app.include_router(socias.router, prefix="/api/v1")
app.include_router(eventos.router, prefix="/api/v1")
app.include_router(drive.router, prefix="/api/v1")

