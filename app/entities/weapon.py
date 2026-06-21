from app.database.connection import db


class Weapon(db.Model):
    """Represents a weapon assigned to an operation."""

    __tablename__ = "weapons"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=False)
    quantity: int = db.Column(db.Integer, nullable=True, default=1)
    operation_id: int = db.Column(
        db.Integer, db.ForeignKey("operations.id"), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "weapon": self.name,
            "quantity": self.quantity if self.quantity is not None else 1,
        }
