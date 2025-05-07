import click
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import CreateModel
from modules.infrastructure.services.admin_services import AdminService
from modules.infrastructure.config.settings import Settings

def get_db():
    settings = Settings()
    postgres_manager = PostgresManager(settings=settings)
    return next(postgres_manager.get_db())

@click.command()
@click.option('--username', required=True, prompt="Admin username")
@click.option('--password', required=True, prompt=True, hide_input=True, confirmation_prompt=True)
def add_admin(username, password):
    """Create a new admin account"""
    db = get_db()
    try:
        admin_service = AdminService()
        admin_service.create_admin(CreateModel(username=username, password=password), db)
        click.secho(f"Admin '{username}' created successfully!")
    except Exception as e:
        click.secho(f"Error: {str(e)}")
        raise click.Abort()