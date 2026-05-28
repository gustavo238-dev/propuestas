from datetime import date

from sqlalchemy import select

from src.domain.entities.enums import CargoStatus, ShipmentType, UserRole
from src.infrastructure.database import models
from src.infrastructure.database.session import Base, SessionLocal, engine
from src.infrastructure.security import hash_password


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_data()


def seed_data() -> None:
    db = SessionLocal()
    try:
        admin = db.scalar(
            select(models.UserModel).where(models.UserModel.email == "admin@empresa-logistica.com")
        )
        if admin is None:
            db.add(
                models.UserModel(
                    email="admin@empresa-logistica.com",
                    password_hash=hash_password("Admin123*"),
                    full_name="Administrador Operativo",
                    role=UserRole.ADMIN.value,
                )
            )

        client = db.scalar(
            select(models.ClientModel).where(models.ClientModel.email == "operaciones@andesimport.com")
        )
        if client is None:
            client = models.ClientModel(
                name="Andes Import S.A.S.",
                tax_id="900123456-7",
                email="operaciones@andesimport.com",
                phone="+57 601 555 0101",
                status="ACTIVE",
            )
            db.add(client)
            db.flush()

        shipment = db.scalar(
            select(models.ShipmentModel).where(models.ShipmentModel.mbl_number == "MAEU9283712")
        )
        if shipment is None:
            shipment = models.ShipmentModel(
                client_id=client.id,
                shipment_type=ShipmentType.DIRECT.value,
                mbl_number="MAEU9283712",
                vessel_name="Maersk Cartagena",
                origin_port="Shanghai",
                destination_port="Cartagena",
                eta=date(2026, 6, 14),
                dta=date(2026, 6, 16),
                cargo_status=CargoStatus.IN_TRANSIT.value,
                goods_description="Repuestos industriales paletizados",
            )
            shipment.containers = [
                models.ContainerModel(
                    container_number="MSCU1234567",
                    container_type="40HC",
                    seal_number="SL-8892",
                    weight_kg=18500,
                    status="IN_TRANSIT",
                )
            ]
            shipment.hbls = [
                models.HblModel(
                    hbl_number="HBL-CO-88421",
                    consignee="Andes Import S.A.S.",
                    notify_party="Agente Aduanero",
                    goods_description="Repuestos industriales",
                )
            ]
            db.add(shipment)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
