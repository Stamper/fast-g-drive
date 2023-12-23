from hashlib import sha256
from secrets import token_hex

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from itsdangerous import BadSignature, Signer
from pydrive2.auth import AuthError

from api.config import BASE_ROOT, SECRET_KEY
from api.gauth import auth_with_code, get_gauth
from api.handlers import redis, router

app = FastAPI()
app.include_router(router, prefix="/api")
signer = Signer(SECRET_KEY, digest_method=sha256)


@app.on_event("shutdown")
async def shutdown_event():
    await redis.aclose()


@app.middleware("http")
async def request_process(request: Request, call_next):
    if request.url.path == "/api/auth":
        session_id = token_hex(8)
        request.state.session_id = session_id
        response = await call_next(request)
        response.set_cookie("session", signer.sign(session_id).decode(), httponly=True)
    elif request.url.path in ("/", "/api/callback", "/favicon.ico"):
        response = await call_next(request)
    else:
        try:
            session_id = signer.unsign(request.cookies.get("session", None))
            gauth_code = await redis.get(session_id)
            request.state.gauth = await auth_with_code(gauth_code)
            response = await call_next(request)
        except (BadSignature, AuthError, ValueError):
            return Response(status_code=401)
    return response


@app.get("/")
async def index():
    with open(BASE_ROOT / "index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)
