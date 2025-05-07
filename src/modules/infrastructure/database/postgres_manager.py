from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from modules.infrastructure.database.interfaces import DatabaseManager
from modules.infrastructure.database.base import Base
from typing import Generator
from modules.infrastructure.database.models import *


class PostgresManager(DatabaseManager):
    def __init__(self, settings):
        self.settings = settings
        self.engine = None
        self.SessionLocal = None

    def create_db_engine(self):
        if not self.engine:
            self.engine = create_engine(
                f"postgresql://{self.settings.database_username}:{self.settings.database_password}"
                f"@{self.settings.database_host}:{self.settings.database_port}/{self.settings.database_name}",
                pool_size=20,
                max_overflow=0,
                pool_pre_ping=True,
            )
        return self.engine

    def get_engine(self):
        return self.create_db_engine()

    def init_db(self):
        Base.metadata.create_all(bind=self.get_engine())

    def get_db(self) -> Generator[Session, None, None]:
        if not self.SessionLocal:
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.get_engine()
            )

        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_session(self) -> Session:
        if not self.SessionLocal:
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.get_engine()
            )
        return self.SessionLocal()
