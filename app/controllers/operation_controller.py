from flask import request, send_file
from flask_restful import Resource
from app.services.operation_service import OperationService, NotFoundError
from app.validators.operation_validator import ValidationError
from app.repositories.operation_repository import DatabaseError
from app.utils.response import success_response, error_response


class OperationListController(Resource):
    """
    ---
    tags:
      - Operations
    """

    def __init__(self) -> None:
        self.service = OperationService()

    def get(self):
        """
        List all police operations
        ---
        tags:
          - Operations
        summary: List all operations
        responses:
          200:
            description: List of operations retrieved successfully
            schema:
              $ref: '#/definitions/SuccessResponse'
            examples:
              application/json:
                success: true
                message: Operations retrieved successfully
                data:
                  - id: 1
                    name: Operação Verão
                    operation_type: OSTENSIVE
                    location: Petrópolis
                    description: Policiamento ostensivo em evento público
                    created_at: "2024-01-15T10:00:00"
                    weapons:
                      - id: 1
                        name: pistola
                        operation_id: 1
                    vehicles:
                      - id: 1
                        name: Viatura 01
                        armored: false
                        operation_id: 1
                    roles:
                      - id: 1
                        name: soldado
                        operation_id: 1
                    investigation_equipments: []
          500:
            description: Internal server error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        operations = self.service.get_all_operations()
        return success_response("Operations retrieved successfully", operations)

    def post(self):
        """
        Create a new police operation
        ---
        tags:
          - Operations
        summary: Create a new operation
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/OperationInput'
        responses:
          201:
            description: Operation created successfully
            schema:
              $ref: '#/definitions/SuccessResponse'
            examples:
              application/json:
                success: true
                message: Operation created successfully
                data:
                  id: 1
                  name: Operação Verão
                  operation_type: OSTENSIVE
                  location: Petrópolis
          400:
            description: Validation error
            schema:
              $ref: '#/definitions/ErrorResponse'
            examples:
              application/json:
                success: false
                error: Uma operação ostensiva deve possuir ao menos 1 viatura.
          500:
            description: Internal server error
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        data = request.get_json(force=True, silent=True) or {}
        operation = self.service.create_operation(data)
        return success_response("Operation created successfully", operation, 201)


class OperationDetailController(Resource):
    """
    ---
    tags:
      - Operations
    """

    def __init__(self) -> None:
        self.service = OperationService()

    def get(self, operation_id: int):
        """
        Get a police operation by ID
        ---
        tags:
          - Operations
        summary: Get operation by ID
        parameters:
          - in: path
            name: operation_id
            type: integer
            required: true
            description: The operation ID
        responses:
          200:
            description: Operation retrieved successfully
            schema:
              $ref: '#/definitions/SuccessResponse'
          404:
            description: Operation not found
            schema:
              $ref: '#/definitions/ErrorResponse'
            examples:
              application/json:
                success: false
                error: Operação com ID 99 não encontrada.
        """
        operation = self.service.get_operation_by_id(operation_id)
        return success_response("Operation retrieved successfully", operation)

    def put(self, operation_id: int):
        """
        Update a police operation
        ---
        tags:
          - Operations
        summary: Update an existing operation
        consumes:
          - application/json
        parameters:
          - in: path
            name: operation_id
            type: integer
            required: true
            description: The operation ID
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/OperationInput'
        responses:
          200:
            description: Operation updated successfully
            schema:
              $ref: '#/definitions/SuccessResponse'
          400:
            description: Validation error
            schema:
              $ref: '#/definitions/ErrorResponse'
          404:
            description: Operation not found
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        data = request.get_json(force=True, silent=True) or {}
        operation = self.service.update_operation(operation_id, data)
        return success_response("Operation updated successfully", operation)

    def delete(self, operation_id: int):
        """
        Delete a police operation
        ---
        tags:
          - Operations
        summary: Delete an operation
        parameters:
          - in: path
            name: operation_id
            type: integer
            required: true
            description: The operation ID
        responses:
          200:
            description: Operation deleted successfully
            schema:
              $ref: '#/definitions/SuccessResponse'
          404:
            description: Operation not found
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        self.service.delete_operation(operation_id)
        return success_response("Operation deleted successfully")


class OperationReportController(Resource):
    """
    ---
    tags:
      - Reports
    """

    def __init__(self) -> None:
        self.service = OperationService()

    def get(self, operation_id: int):
        """
        Generate a PDF report for an operation
        ---
        tags:
          - Reports
        summary: Download operation report as PDF
        produces:
          - application/pdf
        parameters:
          - in: path
            name: operation_id
            type: integer
            required: true
            description: The operation ID
        responses:
          200:
            description: PDF file generated and returned for download
            headers:
              Content-Disposition:
                description: attachment; filename="operation_<id>_report.pdf"
                type: string
          404:
            description: Operation not found
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        pdf_buffer = self.service.generate_report_pdf(operation_id)
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"operation_{operation_id}_report.pdf",
        )
