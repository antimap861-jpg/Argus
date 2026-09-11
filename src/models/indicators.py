from pydantic import BaseModel, Field


class MessageIndicators(BaseModel):
    claimed_organization: str | None = None
    urls: list[str] = Field(default_factory=list)
    urgency_detected: bool = False
    requested_action: str | None = None


class URLIndicators(BaseModel):
    original_url: str
    scheme: str | None = None
    hostname: str | None = None
    port: int | None = None
    path: str | None = None
    query: str | None = None
    fragment: str | None = None
    parsing_error: str | None = None