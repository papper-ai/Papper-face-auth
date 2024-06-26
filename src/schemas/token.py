from pydantic import BaseModel, UUID4, ConfigDict


class JWTPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    user_id: UUID4
    login: str
