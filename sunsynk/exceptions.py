"""Exceptions raised by the Sunsynk API client."""


class SunsynkError(Exception):
    """Base exception for all Sunsynk API client errors."""


class SunsynkAuthenticationError(SunsynkError):
    """The Sunsynk API rejected the username or password."""

    def __init__(self, message: str = 'Invalid username or password'):
        super().__init__(message)


class SunsynkConnectionError(SunsynkError):
    """The Sunsynk API could not be reached or returned an unexpected response."""


# Kept for backwards compatibility with releases before 1.2.0.
InvalidCredentialsException = SunsynkAuthenticationError
