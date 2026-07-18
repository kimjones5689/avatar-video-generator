"""
Talking Photo AI
Error Handler Middleware

Provides consistent error responses across the API.
"""

from flask import jsonify
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class APIError(Exception):
    """
    Base exception for API errors.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "API_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(APIError):
    """
    Validation error.
    """
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
        )


class NotFoundError(APIError):
    """
    Resource not found.
    """
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )


class InternalServerError(APIError):
    """
    Internal server error.
    """
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
        )


def register_error_handlers(app):
    """
    Register error handlers with the Flask app.
    """

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        logger.error("%s: %s", error.error_code, error.message)
        return jsonify(
            {
                "error": error.error_code,
                "message": error.message,
            }
        ), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        logger.warning("Resource not found: %s", error)
        return jsonify(
            {
                "error": "NOT_FOUND",
                "message": "Resource not found.",
            }
        ), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error("Internal server error: %s", error)
        return jsonify(
            {
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error.",
            }
        ), 500
