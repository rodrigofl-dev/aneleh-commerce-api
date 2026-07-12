from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.core import health as health_router

app = FastAPI(
    title=settings.project_name,
    version=settings.api_version,
    # lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router, prefix=settings.api_prefix)


@app.get("/")
def read_root():
    return {"message": "Aneleh Commerce API rodando."}
