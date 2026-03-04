from pydantic import BaseModel


class LinkTokenRequest(BaseModel):
    household_id: str


class LinkTokenResponse(BaseModel):
    link_token: str


class ExchangePublicTokenRequest(BaseModel):
    household_id: str
    public_token: str


class PlaidWebhookPayload(BaseModel):
    webhook_type: str
    webhook_code: str
    item_id: str | None = None
