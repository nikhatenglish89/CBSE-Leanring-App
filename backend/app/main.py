from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import (
    AppError,
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.modules.assistant.router import router as assistant_router
from app.modules.auth.router import router as auth_router
from app.modules.banners.router import router as banners_router
from app.modules.classes.router import router as classes_router
from app.modules.courses.router import router as courses_router
from app.modules.feedback.router import router as feedback_router
from app.modules.groups.router import router as groups_router
from app.modules.interaction.router import router as interaction_router
from app.modules.lessons.router import router as lessons_router
from app.modules.materials.router import router as materials_router
from app.modules.messaging.router import router as messaging_router
from app.modules.practice.router import router as practice_router
from app.modules.subjects.router import chapter_router as chapters_router
from app.modules.subjects.router import router as subjects_router
from app.modules.users.router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="EduSphere CBSE API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(auth_router)
    app.include_router(banners_router)
    app.include_router(users_router)
    app.include_router(classes_router)
    app.include_router(subjects_router)
    app.include_router(chapters_router)
    app.include_router(courses_router)
    app.include_router(lessons_router)
    app.include_router(materials_router)
    app.include_router(practice_router)
    app.include_router(interaction_router)
    app.include_router(messaging_router)
    app.include_router(feedback_router)
    app.include_router(groups_router)
    app.include_router(assistant_router)

    @app.get("/health")
    def health() -> dict:
        return {"success": True, "data": {"status": "ok"}}

    return app


app = create_app()
