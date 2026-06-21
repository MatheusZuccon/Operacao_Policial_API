from datetime import datetime
from app.database.connection import db


class Operation(db.Model):
    """Represents a police operation."""

    __tablename__ = "operations"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operation_number: str = db.Column(db.String(50), unique=True, nullable=True)
    name: str = db.Column(db.String(200), nullable=False)
    operation_type: str = db.Column(db.String(50), nullable=False)
    location: str = db.Column(db.String(300), nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    weapons = db.relationship(
        "Weapon", backref="operation", lazy=True, cascade="all, delete-orphan"
    )
    vehicles = db.relationship(
        "Vehicle", backref="operation", lazy=True, cascade="all, delete-orphan"
    )
    roles = db.relationship(
        "Role", backref="operation", lazy=True, cascade="all, delete-orphan"
    )
    investigation_equipments = db.relationship(
        "InvestigationEquipment",
        backref="operation",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "operation_number": self.operation_number,
            "name": self.name,
            "operation_type": self.operation_type,
            "location": self.location,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "weapons": [w.to_dict() for w in self.weapons],
            "vehicles": [v.to_dict() for v in self.vehicles],
            "roles": [r.to_dict() for r in self.roles],
            "investigation_equipments": [e.to_dict() for e in self.investigation_equipments],
        }
