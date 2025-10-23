import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.database import SessionLocal
from app.models.models import ShareItem

settings = Settings()
STORAGE_PATH = settings.STORAGE_PATH


def cleanup_expired_items():
    db: Optional[Session] = None
    deleted_count = 0
    try:
        db = SessionLocal()
        now = datetime.now(timezone.utc)
        expired_items = (
            db.query(ShareItem)
            .filter(ShareItem.expiry.isnot(None), ShareItem.expiry < now)
            .all()
        )

        count = len(expired_items)

        if count > 0:
            for item in expired_items:
                if item.share_type == "file" and item.content:
                    file_path = os.path.join(STORAGE_PATH, item.content)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"CLEANUP: Deleted file {item.content}.")
                        except OSError as e:
                            print(f"CLEANUP: Failed to delete file {file_path}: {e}")
                    else:
                        print(f"CLEANUP: File not found for deletion: {file_path}")
                db.delete(item)
                deleted_count += 1
            db.commit()
            print(f"CLEANUP: Successfully deleted {deleted_count} expired share items.")
        else:
            print("CLEANUP: No expired items found.")

    except Exception as e:
        print(f"Cleanup Job FAILED. Rolling back transaction: {e}")
        if db:
            db.rollback()

    finally:
        if db:
            db.close()
