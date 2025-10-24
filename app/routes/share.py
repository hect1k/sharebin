from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from slowapi import Limiter
from slowapi.util import get_ipaddr
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies import get_current_user, get_db
from app.models.models import User
from app.services import share_service

settings = Settings()
router = APIRouter()
limiter = Limiter(key_func=get_ipaddr)

DISALLOWED_CODES = [
    "admin",
    "success",
    "register",
    "login",
    "reset",
    "about",
    "terms",
    "health",
    "docs",
    "redoc",
    "openapi.json",
    "favicon.ico",
]


@router.post(
    "/",
    status_code=201,
    responses={
        201: {"description": "File/URL/Text uploaded"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def upload_share_item(
    request: Request,
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    custom_code: Optional[str] = Form(None),
    expiry: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    try:
        content_provided = sum(1 for item in [file, url, text] if item is not None)
        if content_provided != 1:
            raise HTTPException(
                status_code=400,
                detail="You must provide exactly one of: file, url, or text",
            )

        max_expiry = share_service.get_expiry_limit(
            (current_user.plan if current_user else "anon")
        )

        if expiry:
            expiry = expiry * 3600
            if expiry > max_expiry:
                expiry = max_expiry
        else:
            expiry = max_expiry

        if custom_code:
            sanitized_custom_code = share_service.sanitize_custom_code(custom_code)
            code_used = (
                db.query(share_service.ShareItem)
                .filter_by(short_code=sanitized_custom_code)
                .first()
            )
            if code_used or sanitized_custom_code in DISALLOWED_CODES:
                raise HTTPException(
                    status_code=400, detail="Custom code is already in use"
                )
            short_code = sanitized_custom_code
        else:
            short_code = None

        if not short_code:
            short_code = share_service.generate_short_code()
            code_exists = True
            while code_exists or short_code in DISALLOWED_CODES:
                code_exists = (
                    db.query(share_service.ShareItem.short_code)
                    .filter_by(short_code=short_code)
                    .first()
                )
                if code_exists:
                    short_code = share_service.generate_short_code()

        if file:
            if not file.filename:
                raise HTTPException(status_code=400, detail="File name is unknown")

            filename = share_service.generate_unique_filename(file.filename)
            file_size = share_service.get_file_size_in_bytes(file)
            if file_size is None:
                raise HTTPException(
                    status_code=400, detail="File size is unknown or too large"
                )

            if file_size > share_service.get_size_limit(
                "file", (current_user.plan if current_user else "anon")
            ):
                raise HTTPException(
                    status_code=400, detail="File size is too large for your plan"
                )

            filename = share_service.upload_file(
                db, file, filename, short_code, expiry, current_user
            )

            db.commit()

            return JSONResponse(
                status_code=201,
                content={
                    "detail": "File uploaded successfully!",
                    "data": {
                        "filename": filename,
                        "url": f"{settings.DOMAIN}/{short_code}",
                        "expiry": str(expiry / 3600) + " hours",
                    },
                },
            )

        if text:
            text = text.strip()
            if share_service.is_valid_url(text):
                url = share_service.upload_url(
                    db, short_code, text, expiry, current_user
                )
                db.commit()
                return JSONResponse(
                    status_code=201,
                    content={
                        "detail": "URL uploaded successfully!",
                        "data": {
                            "redirect": url,
                            "url": f"{settings.DOMAIN}/{short_code}",
                            "expiry": str(expiry / 3600) + " hours",
                        },
                    },
                )

            max_text_size = share_service.get_size_limit(
                "text", (current_user.plan if current_user else "anon")
            )

            if len(text.encode("utf-8")) > max_text_size:
                raise HTTPException(
                    status_code=400, detail="Text size is too large for your plan"
                )

            text = share_service.upload_text(db, short_code, text, expiry, current_user)
            db.commit()
            return JSONResponse(
                status_code=201,
                content={
                    "detail": "Text uploaded successfully!",
                    "data": {
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "url": f"{settings.DOMAIN}/{short_code}",
                        "expiry": str(expiry / 3600) + " hours",
                    },
                },
            )

        if url:
            url = url.strip()
            if not share_service.is_valid_url(url):
                raise HTTPException(status_code=400, detail="Invalid URL")

            url = share_service.upload_url(db, short_code, url, expiry, current_user)
            db.commit()
            return JSONResponse(
                status_code=201,
                content={
                    "detail": "URL uploaded successfully!",
                    "data": {
                        "redirect": url,
                        "url": f"{settings.DOMAIN}/{short_code}",
                        "expiry": str(expiry / 3600) + " hours",
                    },
                },
            )

        raise HTTPException(
            status_code=400,
            detail="You must provide exactly one of: file, url, or text",
        )

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        print(f"Upload share item error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{short_code}",
    status_code=200,
    responses={
        200: {"description": "OK"},
        302: {"description": "Redirect"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/hour")
async def get_share_item(
    request: Request, short_code: str, db: Session = Depends(get_db)
):
    try:
        share_item = (
            db.query(share_service.ShareItem).filter_by(short_code=short_code).first()
        )
        if not share_item:
            raise HTTPException(status_code=404, detail="Invalid link")

        if share_item.share_type == "file":
            return share_service.serve_file(share_item.content)

        if share_item.share_type == "text":
            return PlainTextResponse(content=share_item.content)

        if share_item.share_type == "url":
            return RedirectResponse(url=share_item.content, status_code=302)

        raise HTTPException(status_code=404, detail="Invalid link")

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        print(f"Get share item error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
