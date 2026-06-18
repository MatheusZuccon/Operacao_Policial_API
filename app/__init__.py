from flask import Flask, jsonify
from flasgger import Swagger
from config import get_config
from app.database.connection import init_db
from app.validators.operation_validator import ValidationError
from app.services.operation_service import NotFoundError
from app.repositories.operation_repository import DatabaseError

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Police Operation API",
        "description": (
            "API para gerenciamento de operações policiais. "
            "Suporta três tipos de operação: Ostensiva, Investigativa e Tática Especial. "
            "Cada tipo possui regras de negócio específicas para armamentos, viaturas e cargos."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "Police Operation API",
            "email": "admin@police-api.dev",
        },
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {
            "name": "Operations",
            "description": "Endpoints para criação, listagem, atualização e exclusão de operações policiais.",
        },
        {
            "name": "Reports",
            "description": "Endpoints para geração de relatórios em PDF.",
        },
    ],
    "definitions": {
        "OperationInput": {
            "type": "object",
            "required": ["name", "operation_type", "location"],
            "properties": {
                "name": {
                    "type": "string",
                    "example": "Operação Verão",
                    "description": "Nome da operação policial",
                },
                "operation_type": {
                    "type": "string",
                    "enum": ["OSTENSIVE", "INVESTIGATIVE", "TACTICAL"],
                    "example": "OSTENSIVE",
                    "description": (
                        "Tipo de operação: "
                        "OSTENSIVE (Ostensiva), "
                        "INVESTIGATIVE (Investigativa), "
                        "TACTICAL (Forças Táticas e Especiais)"
                    ),
                },
                "location": {
                    "type": "string",
                    "example": "Petrópolis",
                    "description": "Localização da operação",
                },
                "description": {
                    "type": "string",
                    "example": "Policiamento ostensivo em evento público",
                    "description": "Descrição detalhada da operação",
                },
                "weapons": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["pistola", "carabina"],
                    "description": (
                        "Lista de armamentos. "
                        "Operações investigativas aceitam somente 'pistola'."
                    ),
                },
                "vehicles": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/VehicleInput"},
                    "example": [{"name": "Viatura 01", "armored": False}],
                    "description": "Lista de viaturas",
                },
                "roles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["soldado", "sargento"],
                    "description": "Lista de cargos/funções",
                },
                "investigation_equipments": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["câmera", "gravador"],
                    "description": "Lista de equipamentos investigativos",
                },
            },
        },
        "VehicleInput": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "type": "string",
                    "example": "Viatura 01",
                },
                "armored": {
                    "type": "boolean",
                    "example": False,
                    "description": "Indica se a viatura é blindada",
                },
            },
        },
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Operation created successfully"},
                "data": {"type": "object"},
            },
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "error": {
                    "type": "string",
                    "example": "Uma operação especial deve possuir ao menos 5 armamentos.",
                },
            },
        },
    },
}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Extensions
    init_db(app)

    # Import all models so Flask-Migrate detects them
    from app.entities import Operation, Weapon, Vehicle, Role, InvestigationEquipment  # noqa: F401

    # Swagger
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # Blueprints
    from app.routes.operation_routes import operations_bp
    app.register_blueprint(operations_bp)

    # Global error handlers
    _register_error_handlers(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        return jsonify({"success": False, "error": exc.message}), 400

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(exc: NotFoundError):
        return jsonify({"success": False, "error": exc.message}), 404

    @app.errorhandler(DatabaseError)
    def handle_database_error(exc: DatabaseError):
        return jsonify({"success": False, "error": exc.message}), 500

    @app.errorhandler(404)
    def handle_404(exc):
        return jsonify({"success": False, "error": "Rota não encontrada."}), 404

    @app.errorhandler(405)
    def handle_405(exc):
        return jsonify({"success": False, "error": "Método HTTP não permitido."}), 405

    @app.errorhandler(500)
    def handle_500(exc):
        return jsonify({"success": False, "error": "Erro interno do servidor."}), 500
