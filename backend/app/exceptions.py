"""
Custom exception types for the Kalibr backend.
"""


class ParseError(Exception):
    """Raised when resume parsing fails after all retries are exhausted."""
