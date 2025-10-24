import contextlib
import os
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_ipaddr

from app import create_tables
from app.dependencies import get_current_user
from app.models.models import User
from app.routes import auth, share
from app.services.scheduler_service import cleanup_expired_items

scheduler = AsyncIOScheduler()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):

    create_tables.init()

    scheduler.add_job(
        cleanup_expired_items,
        "interval",
        minutes=1,
        id="db_cleanup_job",
        next_run_time=datetime.now(),
    )

    scheduler.start()
    print("Background scheduler started and cleanup job is running every minute.")

    yield

    scheduler.shutdown()
    print("Background scheduler shut down.")


app = FastAPI(
    title="shareb.in",
    description="shareb.in is a simple, secure, and easy-to-use file, link, and text sharing platform.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", ""],
    allow_headers=["Authorization", "Content-Type"],
)


async def custom_rate_limit_handler(_: Request, exc: RateLimitExceeded):
    exc_dict = exc.__dict__
    response_content = {
        "detail": "Rate limit exceeded: " + exc_dict.get("detail", ""),
    }

    return JSONResponse(
        content=response_content,
        status_code=429,
    )


limiter = Limiter(key_func=get_ipaddr)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)  # type: ignore


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Web UI"])
async def index():
    file_path = os.path.join("static", "index.html")
    return FileResponse(file_path)


@app.get("/favicon.ico", tags=["Web UI"])
async def docs():
    file_path = os.path.join("static", "favicon.ico")
    return FileResponse(file_path)


@app.get("/success", tags=["Web UI"])
async def success():
    file_path = os.path.join("static", "success.html")
    return FileResponse(file_path)


@app.get("/register", tags=["Web UI"])
async def register():
    file_path = os.path.join("static", "register.html")
    return FileResponse(file_path)


@app.get("/login", tags=["Web UI"])
async def login():
    file_path = os.path.join("static", "login.html")
    return FileResponse(file_path)


@app.get("/reset", tags=["Web UI"])
async def reset():
    file_path = os.path.join("static", "reset.html")
    return FileResponse(file_path)


@app.get("/about", tags=["Web UI"])
async def about():
    file_path = os.path.join("static", "about.html")
    return FileResponse(file_path)


@app.get("/terms", tags=["Web UI"])
async def terms():
    file_path = os.path.join("static", "terms.html")
    return FileResponse(file_path)


@app.get("/health", tags=["Misc."])
@limiter.limit("10/minute")
async def health(
    request: Request, current_user: Optional[User] = Depends(get_current_user)
):
    return {"detail": "shareb.in is healthy!"}


app.include_router(auth.router, tags=["Auth"], prefix="/auth")
app.include_router(share.router, tags=["Share"])
