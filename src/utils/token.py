import jwt
import asyncio
from fastapi import HTTPException, status
from src.config import settings
import logging


async def decode_jwt(
    token: str,
    public_key: str = settings.jwt_auth.public_key_path.read_text(),
    algorithm: str = settings.jwt_auth.algorithm,
) -> dict:
    try:
        payload = await asyncio.to_thread(
            jwt.decode, jwt=token, key=public_key, algorithms=algorithm
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature"
        )
    except Exception as generic_error:
        logging.error(generic_error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload
