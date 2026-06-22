from typing import Optional
from app.repositories.operation_repository import OperationRepository, DatabaseError
from app.validators.operation_validator import OperationValidator, ValidationError
from app.entities.operation import Operation
from app.utils.pdf_generator import generate_operation_pdf
from io import BytesIO


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class OperationService:
    """Orchestrates business logic for police operations."""

    def __init__(self) -> None:
        self.repository = OperationRepository()

    def get_all_operations(self, page: int = 1, page_size: int = 20, search: str = "", sort_by: str = "created_at", sort_dir: str = "desc") -> dict:
        result = OperationRepository.find_all_paginated(page, page_size, search, sort_by, sort_dir)
        return {
            "items": [op.to_dict() for op in result["items"]],
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
            "pages": result["pages"]
        }

    def get_operation_by_id(self, operation_id: int) -> dict:
        operation = OperationRepository.find_by_id(operation_id)
        if not operation:
            raise NotFoundError(
                f"Operação com ID {operation_id} não encontrada."
            )
        return operation.to_dict()

    def create_operation(self, data: dict) -> dict:
        OperationValidator.validate(data)
        operation = OperationRepository.create(data)
        return operation.to_dict()

    def update_operation(self, operation_id: int, data: dict) -> dict:
        operation = OperationRepository.find_by_id(operation_id)
        if not operation:
            raise NotFoundError(
                f"Operação com ID {operation_id} não encontrada."
            )
        OperationValidator.validate(data)
        updated = OperationRepository.update(operation, data)
        return updated.to_dict()

    def delete_operation(self, operation_id: int) -> None:
        operation = OperationRepository.find_by_id(operation_id)
        if not operation:
            raise NotFoundError(
                f"Operação com ID {operation_id} não encontrada."
            )
        OperationRepository.delete(operation)

    def generate_report_pdf(self, operation_id: int) -> BytesIO:
        operation = OperationRepository.find_by_id(operation_id)
        if not operation:
            raise NotFoundError(
                f"Operação com ID {operation_id} não encontrada."
            )
        return generate_operation_pdf(operation)
