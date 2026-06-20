from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.security import get_user_id_from_access_token


PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/auth/telegram"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        token = request.cookies.get("access_token")
        authorization = request.headers.get("Authorization", "")
        if not token and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1]

        if not token:
            return JSONResponse(status_code=401, content={"detail": "Authentication required"})

        try:
            request.state.user_id = get_user_id_from_access_token(token)
        except (ValueError, TypeError):
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        return await call_next(request)
