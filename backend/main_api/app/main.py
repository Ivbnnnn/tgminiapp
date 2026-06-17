from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.logger import logger, setup_logging
from app.api.agents import router as agents_router
from app.api.osago import router as osago_router
from app.api.auth import router as auth_router
from app.middleware import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app:FastAPI):
    setup_logging()
    logger.info("Main API running")
    yield
    logger.info("Main API closed")



app=FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)
app.include_router(agents_router)
app.include_router(osago_router)
app.include_router(auth_router)
