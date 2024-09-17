from sublime import error_message
from logging import exception

class AskCodiException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnknownException(AskCodiException): ...

class WrongUserInputException(AskCodiException): ...

def present_error(title: str, error: AskCodiException):
    exception(f"{title}: {error.message}")
    error_message(f"{title}\n{error.message}")

def present_unknown_error(title: str, error: Exception):
    exception(f"{title}: {error}")
    error_message(f"{title}\n{error}")
