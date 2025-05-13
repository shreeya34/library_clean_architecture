import asyncio
from fastapi import FastAPI
from entrypoints.api.middleware.exception_handlers import ExceptionHandlerMiddleware
from modules.infrastructure.config.settings import settings
from modules.infrastructure.logger import get_logger
from entrypoints.api.routes import admin as admin_routes
from entrypoints.api.routes import member as member_routes
from contextlib import asynccontextmanager
from modules.infrastructure.database.postgres_manager import PostgresManager

db_manager = PostgresManager(settings)


logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(" Starting server...")
    engine = await asyncio.to_thread(db_manager.create_db_engine)
    await asyncio.to_thread(db_manager.init_db)
    app.state.db_engine = engine
    yield
    logger.info("Shutting down server...")


app = FastAPI(lifespan=lifespan)


def init_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(admin_routes.router, tags=["admin"])
    app.include_router(member_routes.router, tags=["member"])

    app.add_middleware(ExceptionHandlerMiddleware)

    return app


app = init_app()
