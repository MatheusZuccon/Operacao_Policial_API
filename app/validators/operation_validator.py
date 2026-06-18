from typing import Any
from app.constants.operation_types import (
    VALID_OPERATION_TYPES,
    OSTENSIVE,
    INVESTIGATIVE,
    TACTICAL,
)
from app.constants.weapons import VALID_WEAPONS, INVESTIGATIVE_ALLOWED_WEAPONS
from app.constants.roles import VALID_ROLES


class ValidationError(Exception):
    """Raised when operation data fails business rule validation."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class OperationValidator:
    """Validates operation payloads against business rules."""

    REQUIRED_FIELDS: list[str] = ["name", "operation_type", "location"]

    @staticmethod
    def validate_required_fields(data: dict) -> None:
        missing = [
            field
            for field in OperationValidator.REQUIRED_FIELDS
            if not data.get(field)
        ]
        if missing:
            fields_str = ", ".join(missing)
            raise ValidationError(
                f"Os seguintes campos obrigatórios estão ausentes: {fields_str}."
            )

    @staticmethod
    def validate_operation_type(operation_type: str) -> None:
        if operation_type not in VALID_OPERATION_TYPES:
            valid_str = ", ".join(VALID_OPERATION_TYPES)
            raise ValidationError(
                f"Tipo de operação inválido: '{operation_type}'. "
                f"Os tipos válidos são: {valid_str}."
            )

    @staticmethod
    def validate_weapons(weapons: list[str]) -> None:
        for weapon in weapons:
            if weapon.lower() not in VALID_WEAPONS:
                valid_str = ", ".join(VALID_WEAPONS)
                raise ValidationError(
                    f"Armamento inválido: '{weapon}'. "
                    f"Os armamentos válidos são: {valid_str}."
                )

    @staticmethod
    def validate_roles(roles: list[str]) -> None:
        for role in roles:
            if role.lower() not in VALID_ROLES:
                valid_str = ", ".join(VALID_ROLES)
                raise ValidationError(
                    f"Cargo inválido: '{role}'. "
                    f"Os cargos válidos são: {valid_str}."
                )

    @staticmethod
    def validate_ostensive(data: dict) -> None:
        weapons: list[str] = data.get("weapons", [])
        vehicles: list[Any] = data.get("vehicles", [])
        roles: list[str] = data.get("roles", [])

        if not vehicles:
            raise ValidationError(
                "Uma operação ostensiva deve possuir ao menos 1 viatura."
            )
        if not weapons:
            raise ValidationError(
                "Uma operação ostensiva deve possuir ao menos 1 armamento."
            )
        if not roles:
            raise ValidationError(
                "Uma operação ostensiva deve possuir ao menos 1 cargo."
            )

    @staticmethod
    def validate_investigative(data: dict) -> None:
        weapons: list[str] = data.get("weapons", [])
        equipments: list[str] = data.get("investigation_equipments", [])
        roles: list[str] = data.get("roles", [])

        if not weapons:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos o armamento 'pistola'."
            )

        for weapon in weapons:
            if weapon.lower() not in INVESTIGATIVE_ALLOWED_WEAPONS:
                raise ValidationError(
                    f"Operações investigativas permitem somente o armamento 'pistola'. "
                    f"Armamento inválido: '{weapon}'."
                )

        if not equipments:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos 1 equipamento investigativo."
            )
        if not roles:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos 1 cargo."
            )

    @staticmethod
    def validate_tactical(data: dict) -> None:
        weapons: list[str] = data.get("weapons", [])
        vehicles: list[Any] = data.get("vehicles", [])
        roles: list[str] = data.get("roles", [])

        if len(vehicles) < 2:
            raise ValidationError(
                "Uma operação de forças táticas e especiais deve possuir ao menos 2 viaturas."
            )
        if len(weapons) < 5:
            raise ValidationError(
                "Uma operação de forças táticas e especiais deve possuir ao menos 5 armamentos."
            )
        if len(roles) < 5:
            raise ValidationError(
                "Uma operação de forças táticas e especiais deve possuir ao menos 5 cargos."
            )

    @classmethod
    def validate(cls, data: dict) -> None:
        """Run all validations for creation or full update."""
        cls.validate_required_fields(data)

        operation_type: str = data.get("operation_type", "")
        cls.validate_operation_type(operation_type)

        weapons: list[str] = data.get("weapons", [])
        roles: list[str] = data.get("roles", [])

        cls.validate_weapons(weapons)
        cls.validate_roles(roles)

        if operation_type == OSTENSIVE:
            cls.validate_ostensive(data)
        elif operation_type == INVESTIGATIVE:
            cls.validate_investigative(data)
        elif operation_type == TACTICAL:
            cls.validate_tactical(data)
