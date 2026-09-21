from pydantic import BaseModel


class TLSEvidence(BaseModel):
    hostname: str
    connection_successful: bool
    certificate_valid: bool | None = None
    issuer: str | None = None
    subject: str | None = None
    not_before: str | None = None
    not_after: str | None = None
    is_self_signed: bool | None = None
    error_message: str | None = None
