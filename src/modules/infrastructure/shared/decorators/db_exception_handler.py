from functools import wraps
from sqlalchemy.orm import Session
import click
from modules.infrastructure.logger import get_logger

logger = get_logger()


def db_exception_handler(operation: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            db = next((arg for arg in args if isinstance(arg, Session)), None)
            if db is None:
                db = kwargs.get("db")

            try:
                return func(*args, **kwargs)
            except Exception as e:
                if db:
                    db.rollback()

                if click.get_current_context(silent=True):
                    click.secho(f"Error: {str(e)}", fg="red")
                    raise click.Abort()
                else:
                    logger.exception(f"Error during {operation}: {str(e)}")
                    raise e

        return wrapper

    return decorator
