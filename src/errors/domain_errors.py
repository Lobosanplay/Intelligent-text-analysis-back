from typing import Any


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    status_code: int = 400

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class DuplicateDocumentError(DomainError):
    code: str = "DOCUMENT_ALREADY_EXISTS"
    status_code: int = 409


class UnsupportedFileTypeError(DomainError):
    code = "UNSUPPORTED_FILE_TYPE"
    status_code: int = 400


class PlanLimitExeceeded(DomainError):
    code = "PLAN_LIMIT_EXECEEDED"
    status_code: int = 400
