from app.database.connection import db


class Weapon(db.Model):
    """Represents a weapon assigned to an operation."""

    __tablename__ = "weapons"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=False)
    operation_id: int = db.Column(
        db.Integer, db.ForeignKey("operations.id"), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "operation_id": self.operation_id,
        }
