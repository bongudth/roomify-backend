import uuid
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, UnauthorizedException
from ...core.schemas import LoginRequest, SignupRequest, Token
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenType,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_token,
)
from ...crud.crud_users import crud_users
from ...schemas.user import UserCreateInternal, UserRead

router = APIRouter(tags=["login"])


@router.post("/signup", response_model=UserRead, status_code=201)
async def sign_up(
    signup_data: SignupRequest,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    email_row = await crud_users.exists(db=db, email=signup_data.email_address)
    if email_row:
        raise DuplicateValueException("Email is already registered")

    # Generate username from email and filter out non-alphanumeric
    import re
    base_username = re.sub(r'[^a-z0-9]', '', signup_data.email_address.split("@")[0].lower())
    if len(base_username) < 2:
        base_username = f"user{uuid.uuid4().hex[:4]}"
    else:
        base_username = base_username[:20]

    # Check if username is taken, append some uuid if needed
    username_row = await crud_users.exists(db=db, username=base_username)
    if username_row:
        username = f"{base_username[:12]}{uuid.uuid4().hex[:8]}"
    else:
        username = base_username
        
    user_internal_dict = {
        "email": signup_data.email_address,
        "username": username,
        "name": username,  # use username as fallback name
        "hashed_password": get_password_hash(signup_data.password)
    }

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)
    
    return created_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    user = await authenticate_user(email=login_data.email, password=login_data.password, db=db)
    if not user:
        raise UnauthorizedException("Wrong email or password.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age
    )

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing.")

    user_data = await verify_token(refresh_token, TokenType.REFRESH, db)
    if not user_data:
        raise UnauthorizedException("Invalid refresh token.")

    new_access_token = await create_access_token(data={"sub": user_data.username_or_email})
    return {"access_token": new_access_token, "token_type": "bearer"}
