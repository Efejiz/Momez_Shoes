import uuid
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class CheckoutSessionRequest(BaseModel):
    amount: float
    currency: str
    success_url: str
    cancel_url: str
    metadata: Optional[Dict[str, Any]] = None

class CheckoutSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"cs_test_{uuid.uuid4().hex}")
    url: str = Field(default_factory=lambda: f"https://checkout.stripe.com/pay/cs_test_{uuid.uuid4().hex}")

class CheckoutStatus(BaseModel):
    payment_status: str = "pending"  # pending, paid, canceled
    amount_total: int = 0  # cents
    currency: str = "usd"

class WebhookResponse(BaseModel):
    event_type: str
    session_id: Optional[str] = None

class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: str):
        self.api_key = api_key
        self.webhook_url = webhook_url
        # simple in-memory map to keep last session amount
        self._sessions: Dict[str, int] = {}

    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSession:
        session = CheckoutSession()
        # store amount in cents
        self._sessions[session.session_id] = int(round(request.amount * 100))
        return session

    async def get_checkout_status(self, session_id: str) -> CheckoutStatus:
        amount_cents = self._sessions.get(session_id, 0)
        return CheckoutStatus(payment_status="pending", amount_total=amount_cents, currency="usd")

    async def handle_webhook(self, body: bytes, signature: Optional[str]) -> WebhookResponse:
        # naive parser for test usage only
        try:
            data = json.loads(body.decode("utf-8"))
            event_type = data.get("type", "unknown")
            session_id = None
            obj = data.get("data", {}).get("object")
            if isinstance(obj, dict):
                session_id = obj.get("id")
            return WebhookResponse(event_type=event_type, session_id=session_id)
        except Exception:
            return WebhookResponse(event_type="unknown", session_id=None)