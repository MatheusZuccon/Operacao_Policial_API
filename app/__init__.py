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

    # Migrate legacy data on startup
    backfill_legacy_data(app)

    return app


def backfill_legacy_data(app) -> None:
    """Backfills legacy database records to conform to the new database schema requirements."""
    with app.app_context():
        from app.database.connection import db
        from app.entities.operation import Operation
        from app.entities.weapon import Weapon
        from app.entities.vehicle import Vehicle
        from app.entities.role import Role
        from app.entities.investigation_equipment import InvestigationEquipment
        import json

        try:
            # 1. Backfill Operations (operation_number)
            ops = Operation.query.filter(Operation.operation_number == None).all()
            for op in ops:
                year = op.created_at.year if op.created_at else 2026
                op.operation_number = f"000{op.id}{year}"

            # 2. Backfill Weapons (quantity)
            weapons = Weapon.query.filter(Weapon.quantity == None).all()
            for w in weapons:
                w.quantity = 1

            # 3. Backfill Investigation Equipments (quantity)
            equips = InvestigationEquipment.query.filter(InvestigationEquipment.quantity == None).all()
            for eq in equips:
                eq.quantity = 1

            # 4. Backfill Vehicles (brand, model, plate)
            vehicles = Vehicle.query.all()
            for v in vehicles:
                if v.brand is None:
                    v.brand = ""
                if v.model is None:
                    v.model = v.name if v.name else ""
                if v.plate is None:
                    v.plate = ""

            # 5. Backfill Roles (quantity, officers)
            roles = Role.query.all()
            for r in roles:
                if r.officers is None:
                    r.officers = json.dumps(["Policial Legado"])
                if r.quantity is None:
                    try:
                        officers_list = json.loads(r.officers)
                        r.quantity = len(officers_list)
                    except Exception:
                        r.quantity = 1

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao migrar dados legados: {str(e)}")


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
