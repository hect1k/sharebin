import app.models.models
from app.db.database import Base, engine


def init():
    print("Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Done. Tables created successfully (or already existed).")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")


if __name__ == "__main__":
    init()
