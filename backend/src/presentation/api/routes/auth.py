from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import TokenResponse
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.session import get_db
from src.infrastructure.security import create_access_token, verify_password
from src.presentation.api.dependencies.security import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(UserModel).where(UserModel.email == form.username))
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )
    token = create_access_token(str(user.id), {"role": user.role, "email": user.email})
    return TokenResponse(access_token=token)


@router.get("/me")
def me(current_user: UserModel = Depends(get_current_user)) -> dict[str, str | bool]:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
