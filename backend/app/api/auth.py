# Feature: Authentication
# Traceability: Infrastructure

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    """Register a new player account and return JWT token."""
    result = service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        region=request.region,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return TokenResponse(
        access_token=result["access_token"],
        player_id=result["player_id"],
        username=result["username"],
        rank=result["rank"],
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)):
    """Authenticate player and return JWT token."""
    result = service.login(username=request.username, password=request.password)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result["message"])
    return TokenResponse(
        access_token=result["access_token"],
        player_id=result["player_id"],
        username=result["username"],
        rank=result["rank"],
    )
