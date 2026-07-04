class WebhookError(Exception):
    """Raised when an error occurs with the webhook"""

class RatelimitError(Exception):
    """Raised when Discord's ratelimit is hit"""

class NotFound(Exception):
    """Raised when something could not be found"""

class BadRequest(Exception):
    """Raised when Discord returns 400: Bad Request"""

class GeneralAPIError(Exception):
    """Raised for general Discord API Errors"""
