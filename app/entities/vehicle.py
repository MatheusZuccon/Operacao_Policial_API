from app.database.connection import db


class Vehicle(db.Model):
    """Represents a vehicle assigned to an operation."""

    __tablename__ = "vehicles"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=False)
    armored: bool = db.Column(db.Boolean, default=False, nullable=False)
    operation_id: int = db.Column(
        db.Integer, db.ForeignKey("operations.id"), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "armored": self.armored,
            "operation_id": self.operation_id,
        }
