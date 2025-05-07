import click
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.infrastructure.config.settings import Settings


@click.command(name="create-tables")
def create_tables():
    """Create database tables using SQLAlchemy."""
    settings = Settings()
    postgres_manager = PostgresManager(settings)
    postgres_manager.init_db()
    click.echo("Tables created successfully.")
