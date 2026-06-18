from flask import Blueprint
from flask_restful import Api
from app.controllers.operation_controller import (
    OperationListController,
    OperationDetailController,
    OperationReportController,
)

operations_bp = Blueprint("operations", __name__)
api = Api(operations_bp)

api.add_resource(OperationListController, "/operations")
api.add_resource(OperationDetailController, "/operations/<int:operation_id>")
api.add_resource(OperationReportController, "/operations/<int:operation_id>/report")
