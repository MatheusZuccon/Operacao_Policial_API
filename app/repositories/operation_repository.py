from typing import Optional
from app.database.connection import db
from app.entities.operation import Operation
from app.entities.weapon import Weapon
from app.entities.vehicle import Vehicle
from app.entities.role import Role
from app.entities.investigation_equipment import InvestigationEquipment


class DatabaseError(Exception):
    """Raised when a database operation fails unexpectedly."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class OperationRepository:
    """Handles all database access for Operation and its related entities."""

    @staticmethod
    def find_all() -> list[Operation]:
        return Operation.query.order_by(Operation.created_at.desc()).all()

    @staticmethod
    def find_all_paginated(page: int = 1, page_size: int = 20, search: str = "") -> dict:
        query = Operation.query
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Operation.name.ilike(search_pattern)) |
                (Operation.operation_number.ilike(search_pattern))
            )
        query = query.order_by(Operation.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return {
            "items": pagination.items,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }

    @staticmethod
    def find_by_id(operation_id: int) -> Optional[Operation]:
        return Operation.query.get(operation_id)

    @staticmethod
    def create(data: dict) -> Operation:
        from datetime import datetime
        try:
            operation = Operation(
                name=data["name"],
                operation_type=data["operation_type"],
                location=data["location"],
                description=data.get("description", ""),
            )
            db.session.add(operation)
            db.session.flush()  # obtain the operation.id before adding children

            # Generate automatically operation_number
            year = datetime.utcnow().year
            operation.operation_number = f"000{operation.id}{year}"

            OperationRepository._add_related_entities(operation, data)

            db.session.commit()
            db.session.refresh(operation)
            return operation
        except Exception as exc:
            db.session.rollback()
            raise DatabaseError(f"Erro ao criar operação: {str(exc)}") from exc

    @staticmethod
    def update(operation: Operation, data: dict) -> Operation:
        try:
            operation.name = data.get("name", operation.name)
            operation.operation_type = data.get("operation_type", operation.operation_type)
            operation.location = data.get("location", operation.location)
            operation.description = data.get("description", operation.description)

            # Replace all related entities
            for weapon in list(operation.weapons):
                db.session.delete(weapon)
            for vehicle in list(operation.vehicles):
                db.session.delete(vehicle)
            for role in list(operation.roles):
                db.session.delete(role)
            for equip in list(operation.investigation_equipments):
                db.session.delete(equip)

            db.session.flush()
            OperationRepository._add_related_entities(operation, data)

            db.session.commit()
            db.session.refresh(operation)
            return operation
        except Exception as exc:
            db.session.rollback()
            raise DatabaseError(f"Erro ao atualizar operação: {str(exc)}") from exc

    @staticmethod
    def delete(operation: Operation) -> None:
        try:
            db.session.delete(operation)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            raise DatabaseError(f"Erro ao excluir operação: {str(exc)}") from exc

    @staticmethod
    def _add_related_entities(operation: Operation, data: dict) -> None:
        """Persist weapons, vehicles, roles and equipments linked to the operation."""
        import json

        for w in data.get("weapons", []):
            name = w.get("weapon", "").lower()
            qty = int(w.get("quantity", 1))
            db.session.add(Weapon(name=name, quantity=qty, operation_id=operation.id))

        for v in data.get("vehicles", []):
            brand = v.get("brand", "")
            model = v.get("model", "")
            plate = v.get("plate", "").upper()
            armored = bool(v.get("armored", False))
            db.session.add(
                Vehicle(
                    brand=brand,
                    model=model,
                    plate=plate,
                    armored=armored,
                    operation_id=operation.id,
                )
            )

        for r in data.get("roles", []):
            name = r.get("role", "").lower()
            qty = int(r.get("quantity", 1))
            officers_list = r.get("officers", [])
            db.session.add(
                Role(
                    name=name,
                    quantity=qty,
                    officers=json.dumps(officers_list),
                    operation_id=operation.id,
                )
            )

        for e in data.get("investigation_equipments", []):
            name = e.get("equipment", "").lower()
            qty = int(e.get("quantity", 1))
            db.session.add(
                InvestigationEquipment(
                    name=name,
                    quantity=qty,
                    operation_id=operation.id,
                )
            )
