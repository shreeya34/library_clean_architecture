import typer
from sqlalchemy.orm import Session
from modules.domain.exceptions.admin.exception import AdminAlreadyExistsError
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import CreateModel
from modules.infrastructure.services.admin_services import AdminService
from modules.infrastructure.config.settings import Settings  

settings = Settings()
postgres_manager = PostgresManager(settings=settings)
db: Session = next(postgres_manager.get_db())

def add_admin(username: str = typer.Option(..., help="Admin username"),
              password: str = typer.Option(..., help="Admin password")):
    admin_data = CreateModel(username=username, password=password)
    admin_service = AdminService()
    try:
        admin_service.create_admin(admin_data, db)
        typer.echo(f"Admin '{username}' created successfully.")
    except AdminAlreadyExistsError as e:
        typer.echo(f"{str(e)}")
