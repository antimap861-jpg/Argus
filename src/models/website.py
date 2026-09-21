from pydantic import BaseModel


class WebsiteEvidence(BaseModel):
    requested_url: str
    fetch_successful: bool
    final_url: str | None = None
    redirect_count: int = 0
    status_code: int | None = None
    title: str | None = None
    has_password_field: bool | None = None
    has_login_form: bool | None = None
    blocked_reason: str | None = None
    error_message: str | None = None
