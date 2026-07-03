class WebhookError(Exception):
    """Raised when an error occurs with the webhook"""
    pass

class RatelimitError(Exception):
    """Raised when Discord's ratelimit is hit"""
    pass

class NotFound(Exception):
    """Raised when something could not be found"""
    pass

class BadRequest(Exception):
    """Raised when Discord returns 400: Bad Request"""
    pass

class GeneralAPIError(Exception):
    """Raised for general Discord API Errors"""
    pass