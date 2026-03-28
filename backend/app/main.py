# Feature: ClutchUp Main Application
# Traceability: All Features

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import tournaments, teams, players

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClutchUp API",
    description="Beginner-Friendly Competitive Gaming Platform API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tournaments.router)
app.include_router(teams.router)
app.include_router(players.router)


@app.get("/")
def root():
    return {
        "message": "ClutchUp API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
