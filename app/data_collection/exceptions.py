class EmptyDataException(Exception):
    """Raised when no input data or no data collected"""
    pass


class SameDayDataException(Exception):
    """Raised when gathered data is from same day"""
    pass
