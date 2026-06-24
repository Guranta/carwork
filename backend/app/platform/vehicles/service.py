from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Vehicle


class VehicleService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self, vin: str, **fields) -> Vehicle:
        v = self.db.execute(select(Vehicle).where(Vehicle.vin == vin)).scalar_one_or_none()
        if v is None:
            v = Vehicle(vin=vin, **{k: val for k, val in fields.items() if val is not None})
            self.db.add(v)
            self.db.commit()
            self.db.refresh(v)
        return v

    def get(self, vehicle_id: int) -> Vehicle | None:
        return self.db.get(Vehicle, vehicle_id)

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[Vehicle], int]:
        total = self.db.query(Vehicle).count()
        rows = (
            self.db.query(Vehicle)
            .order_by(Vehicle.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total
