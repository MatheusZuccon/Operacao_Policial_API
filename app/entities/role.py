from app.database.connection import db


class Role(db.Model):
    """Represents a role/position assigned to an operation."""

    __tablename__ = "roles"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=False)
    quantity: int = db.Column(db.Integer, nullable=True)
    officers: str = db.Column(db.Text, nullable=True)  # JSON serialized list of names
    operation_id: int = db.Column(
        db.Integer, db.ForeignKey("operations.id"), nullable=False
    )

    def to_dict(self) -> dict:
        import json
        try:
            officers_list = json.loads(self.officers) if self.officers else []
        except Exception:
            officers_list = []
        
        qty = self.quantity
        if qty is None:
            qty = len(officers_list) if officers_list else 1
            
        if not officers_list:
            officers_list = ["Policial Legado"]

        return {
            "role": self.name,
            "quantity": qty,
            "officers": officers_list,
        }
