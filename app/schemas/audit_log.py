from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    resource_type: str
    resource_id: str | None
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
