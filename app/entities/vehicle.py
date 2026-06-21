from app.database.connection import db


class Vehicle(db.Model):
    """Represents a vehicle assigned to an operation."""

    __tablename__ = "vehicles"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=True)  # kept for legacy compatibility
    brand: str = db.Column(db.String(20), nullable=True)
    model: str = db.Column(db.String(20), nullable=True)
    plate: str = db.Column(db.String(10), nullable=True)
    armored: bool = db.Column(db.Boolean, default=False, nullable=False)
    operation_id: int = db.Column(
        db.Integer, db.ForeignKey("operations.id"), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "brand": self.brand if self.brand is not None else "",
            "model": self.model if self.model is not None else (self.name if self.name is not None else ""),
            "plate": self.plate if self.plate is not None else "",
            "armored": self.armored,
        }
