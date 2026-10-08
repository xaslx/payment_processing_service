from uuid import UUID

from pydantic import BaseModel, ConfigDict

class OutboxSchema(BaseModel):
    id: UUID
    event_type: str
    payload: dict
    processed: bool

    model_config = ConfigDict(from_attributes=True)
