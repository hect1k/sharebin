from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_ipaddr
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies import get_db_dep
from app.models.models import SuccessResponse, User
from app.services import auth_service, email_service, user_service

settings = Settings()
router = APIRouter()
limiter = Limiter(key_func=get_ipaddr)


@router.post(
    "/register",
    status_code=201,
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
    response_model=SuccessResponse,
)
@limiter.limit("10/minute")
async def register(
    request: Request,
    name: str = Body(None),
    email: str = Body(None),
    password: str = Body(None),
    db: Session = Depends(get_db_dep),
):
    try:
        name = name.strip()
        email = email.strip()
        password = password.strip()

        if not name or not email or not password:
            raise HTTPException(status_code=400, detail="Missing required fields")

        if email.find("@") == -1:
            raise HTTPException(status_code=400, detail="Invalid email")

        if len(password) < 8:
            raise HTTPException(
                status_code=400, detail="Password must be at least 8 characters"
            )

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        user = await user_service.create_user(db, name, email, password)

        token = auth_service.create_verification_token({"sub": email})
        url = settings.DOMAIN + "/auth/verify?token=" + token

        await email_service.send_verification_email(user, url)

        db.commit()

        return JSONResponse(
            status_code=201,
            content={
                "detail": "User registered successfully! Account verification email sent. Please check your spam folder if you don't see it in your inbox.",
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "plan": user.plan,
                },
            },
        )

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        print(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


class EmailRequest(BaseModel):
    email: str


@router.post(
    "/resend",
    status_code=200,
    responses={
        200: {"description": "Verification email resent successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def resend(
    request: Request, payload: EmailRequest, db: Session = Depends(get_db_dep)
):
    try:
        email = payload.email.lower()
        user = user_service.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid email")

        token = auth_service.create_verification_token({"sub": email})
        url = settings.DOMAIN + "/auth/verify?token=" + token

        await email_service.send_verification_email(user, url)

        return JSONResponse(
            status_code=200,
            content={
                "detail": "Verification email resent successfully. Please check your spam folder if you don't see it in your inbox."
            },
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error resending verification email: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/login",
    status_code=200,
    responses={
        200: {"description": "User logged in successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_dep),
):
    try:
        email = form_data.username
        password = form_data.password

        user = user_service.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not user.verified:
            raise HTTPException(status_code=401, detail="Please verify your email!")

        if not auth_service.verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        access_token = auth_service.create_access_token(data={"sub": user.email})
        refresh_token = auth_service.create_refresh_token(data={"sub": user.email})

        return JSONResponse(
            status_code=200,
            content={
                "detail": "User logged in successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "plan": user.plan,
                },
            },
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/refresh",
    status_code=200,
    responses={
        200: {"description": "Access token refreshed successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def refresh(request: Request):
    try:
        header = request.headers.get("Authorization")
        if not header:
            raise HTTPException(status_code=400, detail="Missing authorization header")
        refresh_token = header.split(" ")[1]
        data = auth_service.decode_jwt_token(refresh_token)
        access_token = auth_service.create_access_token(data=data)
        return JSONResponse(
            status_code=200,
            content={
                "detail": "Access token refreshed successfully",
                "access_token": access_token,
                "token_type": "bearer",
            },
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error refreshing access token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/verify",
    status_code=200,
    responses={
        200: {"description": "User verified successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def verify(request: Request, token: str, db: Session = Depends(get_db_dep)):
    try:
        user = auth_service.check_verification_token(db, token)

        if not user or not isinstance(user, User):
            raise HTTPException(status_code=400, detail="Invalid token")

        user.verified = True
        db.add(user)
        db.commit()

        return PlainTextResponse(
            "Account verified successfully. You can now log in with your email and password.",
        )

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        print(f"Error verifying user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/forgot",
    status_code=200,
    responses={
        200: {"description": "Password reset email sent successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def forgot(
    request: Request, payload: EmailRequest, db: Session = Depends(get_db_dep)
):
    try:
        email = payload.email.lower().strip()
        user = user_service.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid email")

        token = auth_service.create_verification_token({"sub": email})
        url = settings.DOMAIN + "/reset?token=" + token

        await email_service.send_password_reset_mail(user, url)

        return JSONResponse(
            status_code=200,
            content={
                "detail": "Password reset email sent successfully. Please check your spam folder if you don't see it in your inbox."
            },
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error sending password reset email: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/reset",
    status_code=200,
    responses={
        200: {"description": "Password reset successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def reset(
    request: Request,
    token: str = Body(None),
    password: str = Body(None),
    db: Session = Depends(get_db_dep),
):
    try:
        password = password.strip()
        if len(password) < 8:
            raise HTTPException(
                status_code=400, detail="Password must be at least 8 characters"
            )

        user = auth_service.check_verification_token(db, token)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid token")

        user.password = auth_service.hash_password(password)
        db.add(user)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"detail": "Password reset successfully"},
        )

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        print(f"Error resetting password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
