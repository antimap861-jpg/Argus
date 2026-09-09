from pydantic import BaseModel, Field


class MessageIndicators(BaseModel):
    claimed_organization: str | None = None
    urls: list[str] = Field(default_factory=list)
    urgency_detected: bool = False
    requested_action: str | None = None