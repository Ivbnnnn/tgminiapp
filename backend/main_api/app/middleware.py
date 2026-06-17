from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.security import get_user_id_from_access_token


PUBLIC_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/auth/logout",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS:
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        access_token = request.cookies.get("access_token")

        if not access_token:
            authorization = request.headers.get("Authorization")

            if authorization and authorization.lower().startswith("bearer "):
                access_token = authorization.split(" ", 1)[1]

        if not access_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Access token cookie missing"},
            )

        try:
            user_id = get_user_id_from_access_token(access_token)
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired access token"},
            )

        request.state.user_id = user_id

        return await call_next(request)
