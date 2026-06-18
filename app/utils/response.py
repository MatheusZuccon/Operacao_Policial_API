from flask import Response, make_response, jsonify
from typing import Any, Optional


def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200,
) -> Response:
    """Build a standardized success response.

    Returns a Flask Response so Flask-RESTful does not attempt to
    re-serialize the object through its own JSON pipeline.
    """
    body: dict = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return make_response(jsonify(body), status_code)


def error_response(error: str, status_code: int = 400) -> Response:
    """Build a standardized error response."""
    return make_response(jsonify({"success": False, "error": error}), status_code)
