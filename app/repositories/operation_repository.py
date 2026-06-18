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
    def find_by_id(operation_id: int) -> Optional[Operation]:
        return Operation.query.get(operation_id)

    @staticmethod
    def create(data: dict) -> Operation:
        try:
            operation = Operation(
                name=data["name"],
                operation_type=data["operation_type"],
                location=data["location"],
                description=data.get("description", ""),
            )
            db.session.add(operation)
            db.session.flush()  # obtain the operation.id before adding children

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
        for weapon_name in data.get("weapons", []):
            db.session.add(Weapon(name=weapon_name.lower(), operation_id=operation.id))

        for vehicle_data in data.get("vehicles", []):
            db.session.add(
                Vehicle(
                    name=vehicle_data.get("name", ""),
                    armored=bool(vehicle_data.get("armored", False)),
                    operation_id=operation.id,
                )
            )

        for role_name in data.get("roles", []):
            db.session.add(Role(name=role_name.lower(), operation_id=operation.id))

        for equip_name in data.get("investigation_equipments", []):
            db.session.add(
                InvestigationEquipment(
                    name=equip_name.lower(), operation_id=operation.id
                )
            )
