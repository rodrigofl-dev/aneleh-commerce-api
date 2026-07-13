from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers

from app.core.health import router as health_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router

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

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)

register_exception_handlers(app)


@app.get("/")
def read_root():
    return {"message": "Aneleh Commerce API is alive!"}
