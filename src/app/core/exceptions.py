class DomainError(Exception):
    """Base para errores de dominio serializables."""
    status_code: int = 500

    def __init__(self, message: str, *, status_code: int | None = None, payload: dict | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload or {}

    def to_airtable_detail(self) -> str:
        base = f"{self.status_code}: {str(self)}"
        if self.payload:
            base += f" | data={self.payload}"
        return base

class NotFoundDomainError(DomainError):
    status_code = 404

class BusinessValidationError(DomainError):
    status_code = 400

class RetryableSystemError(DomainError):
    status_code = 503
