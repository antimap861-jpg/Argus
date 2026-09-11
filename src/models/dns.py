from pydantic import BaseModel, Field


class DNSEvidence(BaseModel):
    hostname: str
    resolved: bool
    ip_addresses: list[str] = Field(default_factory=list)
    error_message: str | None = None
