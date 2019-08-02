"""Exception types."""


class PropertyError(Exception):
    """
    Exception to indicate an issue with a property.
    ORIGIN: webthing.errors.PropertyError
    """
    pass

class ThingNotFoundException(Exception):
    pass

class UnauthorizedException(Exception):
    pass

