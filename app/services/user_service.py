from sqlalchemy.orm import Session

from app.models.models import User
from app.services.auth_service import hash_password


async def create_user(
    db: Session, name: str, email: str, password: str, plan: str = "free"
):
    user = User(name=name, email=email, password=hash_password(password), plan=plan)
    db.add(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
