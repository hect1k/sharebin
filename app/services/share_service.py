import mimetypes
import os
import random
import re
import shutil
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.models import ShareItem, User

settings = Settings()

STORAGE_PATH = settings.STORAGE_PATH

ANON_FILE_SIZE_LIMIT = settings.ANON_FILE_SIZE_LIMIT
FREE_FILE_SIZE_LIMIT = settings.FREE_FILE_SIZE_LIMIT
PAID_FILE_SIZE_LIMIT = settings.PAID_FILE_SIZE_LIMIT

ANON_TEXT_SIZE_LIMIT = settings.ANON_TEXT_SIZE_LIMIT
FREE_TEXT_SIZE_LIMIT = settings.FREE_TEXT_SIZE_LIMIT
PAID_TEXT_SIZE_LIMIT = settings.PAID_TEXT_SIZE_LIMIT

ANON_EXPIRY_LIMIT = settings.ANON_EXPIRY_LIMIT
FREE_EXPIRY_LIMIT = settings.FREE_EXPIRY_LIMIT
PAID_EXPIRY_LIMIT = settings.PAID_EXPIRY_LIMIT


def get_size_limit(file_type: str, plan: str) -> int:
    if file_type == "file":
        if plan == "free":
            return FREE_FILE_SIZE_LIMIT
        elif plan == "paid":
            return PAID_FILE_SIZE_LIMIT
        else:
            return ANON_FILE_SIZE_LIMIT
    else:
        if plan == "free":
            return FREE_TEXT_SIZE_LIMIT
        elif plan == "paid":
            return PAID_TEXT_SIZE_LIMIT
        else:
            return ANON_TEXT_SIZE_LIMIT


def get_expiry_limit(plan: str) -> int:
    if plan == "free":
        return FREE_EXPIRY_LIMIT
    elif plan == "paid":
        return PAID_EXPIRY_LIMIT
    else:
        return ANON_EXPIRY_LIMIT


def get_file_size_in_bytes(file_object: UploadFile) -> Optional[int]:
    if file_object and file_object.size is not None:
        return file_object.size
    return None


def generate_short_code() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))


def sanitize_custom_code(custom_code: str) -> str:
    code = custom_code.strip().lower()
    if code.startswith("/"):
        code = code.lstrip("/")
    code = re.sub(r"[^\w-]", "-", code)
    code = re.sub(r"[-]+", "-", code)
    code = code.strip("-")
    return code


def sanitize_filename(filename: str) -> str:
    filename = filename.strip()
    base, ext = os.path.splitext(filename)
    base = base.split("/")[-1].split("\\")[-1]
    base = base.lower()
    base = re.sub(r"[^\w\.\-]+", "-", base)
    base = re.sub(r"[-]+", "-", base)
    base = base.strip("-")
    if not base:
        return f"unnamed{ext}"
    return f"{base}{ext}"


def generate_unique_filename(filename: str) -> str:
    filename = sanitize_filename(filename)
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(f"{STORAGE_PATH}/{filename}"):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename


def calculate_expiry_datetime(expiry_seconds: float) -> datetime:
    now_utc = datetime.now(timezone.utc)
    duration = timedelta(seconds=expiry_seconds)
    expiry_dt = now_utc + duration
    return expiry_dt


def upload_file(
    db: Session,
    file: UploadFile,
    filename: str,
    short_code: str,
    expiry: float,
    user: Optional[User],
) -> str:
    unique_filename = generate_unique_filename(filename)
    full_path = f"{STORAGE_PATH}/{unique_filename}"
    file_saved = False

    share_item = ShareItem(
        short_code=short_code,
        share_type="file",
        content=unique_filename,
        expiry=calculate_expiry_datetime(expiry),
    )

    if user:
        share_item.user_id = user.id

    db.add(share_item)

    try:
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_saved = True
        return unique_filename

    except Exception as e:
        print(f"File upload failed: {e}")
        if file_saved and os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"Cleaned up partial file: {full_path}")
            except OSError as cleanup_e:
                print(
                    f"FATAL: Failed to clean up file {full_path} after error: {cleanup_e}"
                )
        raise e

    finally:
        file.file.close()


def get_file_mimetype(filename: str) -> Optional[str]:
    mimetype, _ = mimetypes.guess_type(filename)
    return mimetype


def is_image(mimetype: Optional[str]) -> bool:
    if mimetype is not None and mimetype.startswith("image/"):
        return True
    return False


def serve_file(filename: str) -> FileResponse:
    file_path = os.path.join(STORAGE_PATH, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    mimetype = get_file_mimetype(filename)
    if is_image(mimetype):
        content_disposition = f'inline; filename="{filename}"'
        media_type = mimetype
    else:
        content_disposition = f'attachment; filename="{filename}"'
        media_type = mimetype if mimetype else "application/octet-stream"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={"Content-Disposition": content_disposition},
    )


def is_valid_url(url_string: str) -> bool:
    url_string = url_string.strip()

    if " " in url_string:
        return False

    if url_string.startswith("http://") or url_string.startswith("https://"):
        return True
    return False


def sanitize_paste_content(content: str) -> str:
    sanitized_content = content.strip()
    sanitized_content = sanitized_content.replace("<", "&lt;").replace(">", "&gt;")
    sanitized_content = sanitized_content.replace("\x00", "")
    return sanitized_content


def upload_text(
    db: Session, short_code: str, text: str, expiry: float, user: Optional[User]
):
    text = sanitize_paste_content(text)
    share_item = ShareItem(
        short_code=short_code,
        share_type="text",
        content=text,
        expiry=calculate_expiry_datetime(expiry),
    )
    if user:
        share_item.user_id = user.id
    db.add(share_item)
    return text


def upload_url(
    db: Session, short_code: str, url: str, expiry: float, user: Optional[User]
):
    share_item = ShareItem(
        short_code=short_code,
        share_type="url",
        content=url,
        expiry=calculate_expiry_datetime(expiry),
    )
    if user:
        share_item.user_id = user.id
    db.add(share_item)
    return url
