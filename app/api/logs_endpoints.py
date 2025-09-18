from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from app.core.logger import LOG_FILE
import asyncio, os

router = APIRouter(tags=["Admin Pannel"])

@router.get("/logs", response_class=PlainTextResponse)
def tail_logs(n: int = 200):
    if not LOG_FILE.exists():
        return ""
    with LOG_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    n = max(1, min(n, 5000))
    return "".join(lines[-n:])