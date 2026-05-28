from sqlalchemy.orm import Session

from src.domain.entities.enums import UserRole
from src.infrastructure.database.models import UserModel
from src.infrastructure.security import hash_password


def test_login_returns_jwt_and_me_returns_current_user(client, db_session: Session) -> None:
    user = UserModel(
        email="admin@empresa-logistica.com",
        password_hash=hash_password("Admin123*"),
        full_name="Administrador Operativo",
        role=UserRole.ADMIN.value,
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "Admin123*"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["email"] == user.email
    assert me_response.json()["role"] == UserRole.ADMIN.value
