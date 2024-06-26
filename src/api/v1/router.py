from fastapi import APIRouter, WebSocket, Depends
from .dependencies import parse_jwt_bearer, get_face_service
from src.schemas.token import JWTPayload
from src.services.face_service import FaceService
from typing import Annotated


router = APIRouter(prefix="/face-auth", tags=["Face Authentication"])


@router.websocket("/realtime/detection")
async def face_detection(
    websocket: WebSocket,
    token_payload: Annotated[JWTPayload, Depends(parse_jwt_bearer)],
    face_service: Annotated[FaceService, Depends(get_face_service)],
) -> None:
    await websocket.accept()
    await face_service.detect_face(websocket)
    return
