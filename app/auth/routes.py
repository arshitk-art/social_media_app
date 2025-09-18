from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List
# from app.database import get_session  # Your session dependency
from app.users.models import User  # Your SQLModel user model
# from app.users.schemas import UserCreate, UserRead  # Pydantic schemas
from app.auth.schemas import LoginSchema,ResponseSchema
from app.users.crud import UserServiceHandler
from deps import get_session
from passlib.context import CryptContext
from app.auth.auth_handler import sign_jwt, decode_jwt, create_access_token
from app.auth.auth_handler import INVALID_TOKEN
from app.users.schemas import CreateUserSchema


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class AuthAPIWrapper:
    @router.post("/login")
    def login(login_data: LoginSchema, session: Session = Depends(get_session)):
        if not login_data.username and not login_data.email:
            return ResponseSchema(message="Username or Email is required", status="error", status_code=400)
        if not login_data.password:
            return ResponseSchema(message="Password is required", status="error", status_code=400)

        handler = UserServiceHandler(session)

        # Find user
        user = None
        if login_data.username:
            user = handler.get_user_by_id(login_data.username)
        elif login_data.email:
            user = handler.get_user_by_email(login_data.email)

        if not user:
            return ResponseSchema(message="User not found", status="error", status_code=404)

        if not pwd_context.verify(login_data.password, user.password_hash):
            return ResponseSchema(message="Invalid password", status="error", status_code=401)

        tokens = sign_jwt(str(user.id))
        return ResponseSchema(message="Login successful", status="success", status_code=200, data_dict=tokens)

    @router.post("/logout", response_model=ResponseSchema)
    def logout(token: str, session: Session = Depends(get_session)):
        handler = UserServiceHandler(session)
        INVALID_TOKEN.add(token)  # you implement
        return ResponseSchema(
            message="Successfully logged out",
            status="success",
            status_code=200
        )
    
    @router.post("/register", response_model=ResponseSchema)
    def register(user_data: CreateUserSchema, session: Session = Depends(get_session)):
        handler = UserServiceHandler(session)
        existing_user = handler.get_user_by_email(user_data.email)
        if existing_user:
            raise ResponseSchema(status_code=400, message="Email already registered", status="error")
        
        user_data.password = pwd_context.hash(user_data.password)
        new_user = handler.create_user(user_data)
        tokens = sign_jwt(str(new_user.id))
        return ResponseSchema(
            message="User registered successfully",
            status="success",
            status_code=201,
            data_dict=tokens
        )
    
    @router.post("/refresh", response_model=ResponseSchema)
    def refresh_token(refresh_token: str, session: Session = Depends(get_session)):
        try:
            payload = decode_jwt(refresh_token, session)
            if payload["type"] != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            new_access_token = create_access_token(payload["user_id"])
            return ResponseSchema(
                message="Token refreshed",
                status="success",
                status_code=200,
                data={"access_token": new_access_token}
            )
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    

