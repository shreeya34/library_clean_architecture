from modules.infrastructure.config.settings import Settings
from modules.infrastructure.database.postgres_manager import PostgresManager


def get_db():
    settings = Settings()
    postgres_manager = PostgresManager(settings=settings)
    return next(postgres_manager.get_db())
