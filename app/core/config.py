import os

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

load_dotenv()


class Settings(BaseModel):

    PORT: int = int(os.getenv("PORT", 8000))
    DOMAIN: str = os.getenv("DOMAIN", "https://shareb.in")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
    JWT_REFRESH_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", 30))

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "vaultx_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./data")
    LOG_PATH: str = os.getenv("LOG_PATH", "./logs")

    MAIL_HOST: str = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "login")
    MAIL_PASSWORD: SecretStr = SecretStr(
        os.getenv("MAIL_PASSWORD", "your_email_password")
    )
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@shareb.in")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Quagmire from sharebin")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", True) in ["true", "True"]
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", False) in ["true", "True"]

    ANON_FILE_SIZE_LIMIT: int = int(
        os.getenv("ANON_FILE_SIZE_LIMIT", 52428800)
    )  # 50 MB
    FREE_FILE_SIZE_LIMIT: int = int(
        os.getenv("FREE_FILE_SIZE_LIMIT", 262144000)
    )  # 250 MB
    PAID_FILE_SIZE_LIMIT: int = int(
        os.getenv("PAID_FILE_SIZE_LIMIT", 5368709120)
    )  # 5 GB

    ANON_TEXT_SIZE_LIMIT: int = int(os.getenv("ANON_TEXT_SIZE_LIMIT", 1048576))  # 1 MB
    FREE_TEXT_SIZE_LIMIT: int = int(os.getenv("FREE_TEXT_SIZE_LIMIT", 5242880))  # 5 MB
    PAID_TEXT_SIZE_LIMIT: int = int(
        os.getenv("PAID_TEXT_SIZE_LIMIT", 10485760)
    )  # 10 MB

    ANON_EXPIRY_LIMIT: int = int(os.getenv("ANON_EXPIRY_LIMIT", 86400))  # 1 day
    FREE_EXPIRY_LIMIT: int = int(os.getenv("FREE_EXPIRY_LIMIT", 604800))  # 7 days
    PAID_EXPIRY_LIMIT: int = int(os.getenv("PAID_EXPIRY_LIMIT", 2592000))  # 30 days

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
