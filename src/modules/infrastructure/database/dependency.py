from modules.infrastructure.config import settings
from modules.infrastructure.database.postgres_manager import PostgresManager
from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.orm import Session

db_manager = PostgresManager(settings)


db_dependency = Annotated[Session, Depends(db_manager.get_db)]


def get_db_from_app(request: Request):
    engine = request.app.state.db_engine
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()
