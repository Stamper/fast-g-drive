from pathlib import Path

from anyio import to_thread
from furl import furl
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from api.config import API_BASE_URL


async def get_gauth():
    gauth = await to_thread.run_sync(GoogleAuth)
    await to_thread.run_sync(
        gauth.LoadClientConfigFile,
        str(Path(__file__).parent.parent.parent / "client_secrets.json"),
    )
    return gauth


async def get_google_auth_url(session_id: str):
    gauth = await get_gauth()
    gauth_url = furl(await to_thread.run_sync(gauth.GetAuthUrl))
    gauth_url.args["redirect_uri"] = f"{API_BASE_URL}/callback"
    gauth_url.args["state"] = session_id
    return gauth_url.url


async def auth_with_code(code: str):
    gauth = await get_gauth()
    await to_thread.run_sync(gauth.Auth, code)
    return gauth


async def get_files(gauth: GoogleAuth):
    drive = await to_thread.run_sync(GoogleDrive, gauth)
    file_list = await to_thread.run_sync(drive.ListFile, {'q': "'root' in parents and trashed=false"})
    files = await to_thread.run_sync(file_list.GetList)
    return {f["id"]: f["title"] for f in files}
