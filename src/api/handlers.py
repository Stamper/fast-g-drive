import redis.asyncio as redis
from fastapi import APIRouter, Request

from api.gauth import get_google_auth_url, get_files
from api.models import FileModel

router = APIRouter()
redis = redis.Redis()


@router.get("/auth")
async def authenticate(request: Request):
    return await get_google_auth_url(request.state.session_id)


@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    session_id = request.query_params.get("state")
    await redis.set(session_id, code)
    return "Authentication successful"


@router.get("/files")
async def files(request: Request) -> list[FileModel]:
    files_list = await get_files(request.state.gauth)
    return [FileModel(id=k, title=v) for k, v in files_list.items()]
