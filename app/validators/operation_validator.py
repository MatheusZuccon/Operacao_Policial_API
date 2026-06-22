import re
from typing import Any, Optional
from app.constants.operation_types import (
    VALID_OPERATION_TYPES,
    OSTENSIVE,
    INVESTIGATIVE,
    TACTICAL,
)
from app.constants.weapons import VALID_WEAPONS, INVESTIGATIVE_ALLOWED_WEAPONS
from app.constants.roles import VALID_ROLES
from app.constants.equipments import VALID_EQUIPMENTS


class ValidationError(Exception):
    """Raised when operation data fails business rule validation."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


# Regex that matches strings containing at least one letter (accented included).
# Rejects strings composed only of digits, spaces and/or special characters.
_HAS_LETTER_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")


def _validate_text_field(value: Any, field_label: str, max_length: Optional[int] = None) -> str:
    """
    Validate a generic text field:
      - Must be a non-empty string.
      - Must have at least 3 characters after stripping whitespace.
      - Must contain at least one letter (no pure numbers / special-char strings).
      - Optionally enforces a maximum length.

    Returns the stripped string on success; raises ValidationError on failure.
    """
    if not value or not isinstance(value, str):
        raise ValidationError(f"O campo '{field_label}' é obrigatório.")

    stripped = value.strip()

    if len(stripped) < 3:
        raise ValidationError(
            f"O campo '{field_label}' deve ter no mínimo 3 caracteres."
        )

    if not _HAS_LETTER_RE.search(stripped):
        raise ValidationError(
            f"O campo '{field_label}' não pode conter apenas números ou caracteres especiais. "
            f"Informe um texto com ao menos uma letra."
        )

    if max_length is not None and len(stripped) > max_length:
        raise ValidationError(
            f"O campo '{field_label}' deve ter no máximo {max_length} caracteres."
        )

    return stripped


class OperationValidator:
    """Validates operation payloads against business rules."""

    REQUIRED_FIELDS: list[str] = ["name", "operation_type", "location"]
    PLATE_REGEX = re.compile(r"^[A-Za-z]{3}\d[A-Za-z0-9]\d{2}$")

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
    def validate_quantity(qty: Any, field_name: str, min_value: int = 1) -> int:
        """Validate an integer quantity field. Only pure numeric values are accepted."""
        if qty is None:
            raise ValidationError(f"O campo quantidade de '{field_name}' é obrigatório.")
        try:
            val = int(qty)
        except (ValueError, TypeError):
            raise ValidationError(f"A quantidade de '{field_name}' deve ser um número inteiro.")

        if val < min_value or val > 99:
            if min_value == 1:
                raise ValidationError(f"A quantidade de '{field_name}' deve estar entre 1 e 99.")
            else:
                raise ValidationError(
                    f"A quantidade de '{field_name}' deve estar entre {min_value} e 99."
                )
        return val

    @staticmethod
    def validate_weapons(weapons: list[dict]) -> None:
        if not isinstance(weapons, list):
            raise ValidationError("O campo armamentos deve ser uma lista.")
        for item in weapons:
            if not isinstance(item, dict):
                raise ValidationError("Cada armamento deve ser informado como um objeto com 'weapon' e 'quantity'.")
            weapon = item.get("weapon")
            if not weapon:
                raise ValidationError("O nome do armamento é obrigatório.")
            if weapon.lower() not in VALID_WEAPONS:
                valid_str = ", ".join(VALID_WEAPONS)
                raise ValidationError(
                    f"Armamento inválido: '{weapon}'. "
                    f"Os armamentos válidos são: {valid_str}."
                )
            qty = item.get("quantity")
            OperationValidator.validate_quantity(qty, f"armamento {weapon}")

    @staticmethod
    def validate_roles(roles: list[dict]) -> None:
        if not isinstance(roles, list):
            raise ValidationError("O campo cargos deve ser uma lista.")
        for item in roles:
            if not isinstance(item, dict):
                raise ValidationError("Cada cargo deve ser informado como um objeto com 'role', 'quantity' e 'officers'.")
            role = item.get("role")
            if not role:
                raise ValidationError("O nome do cargo é obrigatório.")
            if role.lower() not in VALID_ROLES:
                valid_str = ", ".join(VALID_ROLES)
                raise ValidationError(
                    f"Cargo inválido: '{role}'. "
                    f"Os cargos válidos são: {valid_str}."
                )

            qty = item.get("quantity")
            qty_val = OperationValidator.validate_quantity(qty, f"cargo {role}")

            officers = item.get("officers")
            if not isinstance(officers, list):
                raise ValidationError(f"A lista de policiais para o cargo '{role}' é obrigatória e deve ser uma lista.")

            if len(officers) != qty_val:
                raise ValidationError(
                    f"A quantidade ({qty_val}) de policiais para o cargo '{role}' deve ser igual ao número de policiais cadastrados ({len(officers)})."
                )

            for officer in officers:
                if not officer or not isinstance(officer, str) or not officer.strip():
                    raise ValidationError(f"O nome do policial no cargo '{role}' é obrigatório.")
                # Validate officer name: min 3 chars, must have a letter, max 150 chars
                _validate_text_field(officer, f"policial no cargo '{role}'", max_length=150)

    @staticmethod
    def validate_vehicles(vehicles: list[dict]) -> None:
        if not isinstance(vehicles, list):
            raise ValidationError("O campo viaturas deve ser uma lista.")

        plates = []
        for item in vehicles:
            if not isinstance(item, dict):
                raise ValidationError("Cada viatura deve ser informada como um objeto com 'brand', 'model', 'plate' e 'armored'.")

            brand = item.get("brand")
            _validate_text_field(brand, "marca da viatura", max_length=20)

            model = item.get("model")
            _validate_text_field(model, "modelo da viatura", max_length=20)

            plate = item.get("plate")
            if not plate or not isinstance(plate, str) or not plate.strip():
                raise ValidationError("A placa da viatura é obrigatória.")

            plate_clean = plate.strip().upper()
            if not OperationValidator.PLATE_REGEX.match(plate_clean):
                raise ValidationError(
                    f"A placa da viatura '{plate}' é inválida. Formatos aceitos: ABC1234 (antigo) ou ABC1D23 (Mercosul)."
                )

            if plate_clean in plates:
                raise ValidationError(f"A placa '{plate_clean}' está duplicada nesta operação.")
            plates.append(plate_clean)

    @staticmethod
    def validate_equipments(equipments: list[dict]) -> None:
        if not isinstance(equipments, list):
            raise ValidationError("O campo equipamentos investigativos deve ser uma lista.")
        for item in equipments:
            if not isinstance(item, dict):
                raise ValidationError("Cada equipamento deve ser informado como um objeto com 'equipment' e 'quantity'.")
            equipment = item.get("equipment")
            if not equipment:
                raise ValidationError("O nome do equipamento é obrigatório.")
            if equipment.lower() not in VALID_EQUIPMENTS:
                valid_str = ", ".join(VALID_EQUIPMENTS)
                raise ValidationError(
                    f"Equipamento investigativo inválido: '{equipment}'. "
                    f"Os equipamentos válidos são: {valid_str}."
                )
            qty = item.get("quantity")
            OperationValidator.validate_quantity(qty, f"equipamento {equipment}")

    @staticmethod
    def validate_ostensive(data: dict) -> None:
        weapons: list[dict] = data.get("weapons", [])
        vehicles: list[dict] = data.get("vehicles", [])
        roles: list[dict] = data.get("roles", [])

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
        """
        Investigative operations rules:
          - Requires at least 1 pistol (weapon='pistola'), with quantity >= 1.
          - Only 'pistola' is allowed as weapon.
          - Requires at least 1 investigative equipment.
          - Requires at least 1 role.
          - Requires at least 1 vehicle (vehicle quantity >= 1).
        """
        weapons: list[dict] = data.get("weapons", [])
        equipments: list[dict] = data.get("investigation_equipments", [])
        roles: list[dict] = data.get("roles", [])
        vehicles: list[dict] = data.get("vehicles", [])

        if not weapons:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos o armamento 'pistola'."
            )

        for item in weapons:
            weapon_name = item.get("weapon", "")
            if weapon_name.lower() not in INVESTIGATIVE_ALLOWED_WEAPONS:
                raise ValidationError(
                    f"Operações investigativas permitem somente o armamento 'pistola'. "
                    f"Armamento inválido: '{weapon_name}'."
                )

        if not equipments:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos 1 equipamento investigativo."
            )
        if not roles:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos 1 cargo."
            )

        # New rule: investigative operations require at least 1 vehicle
        if not vehicles:
            raise ValidationError(
                "Uma operação investigativa deve possuir ao menos 1 viatura."
            )

    @staticmethod
    def validate_tactical(data: dict) -> None:
        weapons: list[dict] = data.get("weapons", [])
        vehicles: list[dict] = data.get("vehicles", [])
        roles: list[dict] = data.get("roles", [])

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

        name = data.get("name", "")
        _validate_text_field(name, "nome da operação", max_length=150)

        location = data.get("location", "")
        _validate_text_field(location, "localização", max_length=150)

        description = data.get("description", "")
        if description and isinstance(description, str) and len(description) > 500:
            raise ValidationError("A descrição deve ter no máximo 500 caracteres.")

        operation_type: str = data.get("operation_type", "")
        cls.validate_operation_type(operation_type)

        weapons: list[dict] = data.get("weapons", [])
        roles: list[dict] = data.get("roles", [])
        vehicles: list[dict] = data.get("vehicles", [])
        equipments: list[dict] = data.get("investigation_equipments", [])

        cls.validate_weapons(weapons)
        cls.validate_roles(roles)
        cls.validate_vehicles(vehicles)
        cls.validate_equipments(equipments)

        if operation_type == OSTENSIVE:
            cls.validate_ostensive(data)
        elif operation_type == INVESTIGATIVE:
            cls.validate_investigative(data)
        elif operation_type == TACTICAL:
            cls.validate_tactical(data)
