from fastapi import APIRouter, Depends, Request, Response, status, HTTPException

from app.schemas import AgentCreate, AgentLogin
from app.services.agents import AgentService
from app.deps import get_agent_service


router = APIRouter(prefix="/auth", tags=["Auth"])


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str | None = None,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 15,
    )

    if refresh_token is not None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def signup(
    data: AgentCreate,
    response: Response,
    agent_service: AgentService = Depends(get_agent_service),
):
    tokens = await agent_service.signup(data)

    set_auth_cookies(
        response=response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {"detail": "Agent created"}


@router.post("/login")
async def login(
    data: AgentLogin,
    response: Response,
    agent_service: AgentService = Depends(get_agent_service),
):
    tokens = await agent_service.login(data)

    set_auth_cookies(
        response=response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {"detail": "Logged in"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    agent_service: AgentService = Depends(get_agent_service),
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie missing",
        )

    access_token = await agent_service.refresh(refresh_token)

    if access_token == "no":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    set_auth_cookies(
        response=response,
        access_token=access_token,
    )

    return {"detail": "Token refreshed"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"detail": "Logged out"}