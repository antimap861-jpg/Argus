from pydantic import BaseModel, Field


class RegistrationEvidence(BaseModel):
    hostname: str
    lookup_successful: bool
    registrar: str | None = None
    creation_date: str | None = None
    expiration_date: str | None = None
    nameservers: list[str] = Field(default_factory=list)
    error_message: str | None = None
