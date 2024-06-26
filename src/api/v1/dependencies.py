from typing import Annotated
from src.schemas.token import JWTPayload
from src.utils.token import decode_jwt
from src.services.face_service import FaceService
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

http_bearer = HTTPBearer()


async def parse_jwt_bearer(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> JWTPayload:
    token = credentials.credentials
    dict_payload = await decode_jwt(token=token)
    payload = JWTPayload.model_validate(dict_payload)
    return payload


async def get_face_service() -> FaceService:
    return FaceService()
