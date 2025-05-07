from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.infrastructure.config.settings import Settings
import typer

app = typer.Typer()


@app.command("create-tables")
def create_tables():
    """Create database tables using SQLAlchemy."""
    settings = Settings()
    postgres_manager = PostgresManager(settings)
    postgres_manager.init_db()
    typer.echo("Tables created successfully.")
