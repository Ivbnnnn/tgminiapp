import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.catalog import router as catalog_router
from app.api.favorites import router as favorites_router
from app.api.products import router as products_router
from app.api.users import router as users_router
from app.api.sellers import router as sellers_router
from app.core.config import settings
from app.core.logger import logger, setup_logging
from app.middleware import AuthMiddleware
from app.services.storage import object_storage


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    for attempt in range(10):
        try:
            await object_storage.ensure_bucket()
            break
        except Exception:
            if attempt == 9:
                raise
            logger.warning("MinIO is not ready, retrying")
            await asyncio.sleep(2)
    logger.info("Marketplace API started")
    yield
    logger.info("Marketplace API stopped")


app = FastAPI(title="Telegram Marketplace API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(catalog_router)
app.include_router(products_router)
app.include_router(favorites_router)
app.include_router(sellers_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
