"""Exceptions raised by the Sunsynk API client."""


class SunsynkError(Exception):
    """Base exception for all Sunsynk API client errors."""


class SunsynkAuthenticationError(SunsynkError):
    """The Sunsynk API rejected the username or password."""

    def __init__(self, message: str = 'Invalid username or password'):
        super().__init__(message)


class SunsynkConnectionError(SunsynkError):
    """The Sunsynk API could not be reached or returned an unexpected response."""


class SunsynkApiError(SunsynkError):
    """The Sunsynk API was reached but reported that the request failed.

    This is raised when the API responds with ``success: false``. Unlike
    ``SunsynkConnectionError`` it is not a transient network problem, so
    retrying the same request is unlikely to help.
    """

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code


# Kept for backwards compatibility with releases before 1.2.0.
InvalidCredentialsException = SunsynkAuthenticationError
