# app/auth/auth_handler.py

import time
from typing import Dict
import jwt
import os
from config import settings
from app.users.crud import UserServiceHandler
from sqlmodel import Session
from uuid import UUID
from asgiref.sync import async_to_sync


SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_SECONDS = settings.ACCESS_TOKEN_EXPIRE_SECONDS
ALGORITHM = settings.ALGORITHM
INVALID_TOKEN = set()

def sign_jwt(user_id: UUID) -> Dict[str, str]:
    access_payload = {
        "user_id": user_id,
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS,
        "type": "access"
    }
    refresh_payload = {
        "user_id": user_id,
        "exp": time.time() + (60 * 60 * 24 * 7),  # 7 days
        "type": "refresh"
    }

    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "refresh_token": refresh_token}

def create_access_token(user_id: UUID) -> str:
    access_payload = {
        "user_id": user_id,
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS,
        "type": "access"
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token}

def decode_jwt(token: str, session: Session) -> dict | None:
    try:
        handler = UserServiceHandler(session=session)
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(decoded_token)
        if decoded_token["exp"] < time.time():
            print(1)
            return None

        user_id = decoded_token.get("user_id")
        if not user_id:
            print(0)
            return None

        user = async_to_sync(handler.get_user_by_id)(user_id=user_id)
        if not user or not user.is_active:
            print(2)
            return None

        return decoded_token  # valid payload
    except Exception:
        return None

