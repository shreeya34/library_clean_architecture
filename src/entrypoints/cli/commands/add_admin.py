import typer
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import CreateModel
from modules.infrastructure.services.admin_services import add_admin as core_add_admin
from modules.infrastructure.config.settings import Settings  
# Initialize settings
settings = Settings()


postgres_manager = PostgresManager(settings=settings)
db: Session = next(postgres_manager.get_db())

def add_admin(username: str = typer.Option(..., help="Admin username"),
              password: str = typer.Option(..., help="Admin password")):
    admin_data = CreateModel(username=username, password=password)
    core_add_admin(admin_data, db)
    typer.echo(f"Admin '{username}' created successfully.")
