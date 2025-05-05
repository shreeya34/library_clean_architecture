import typer
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import AdminLogins
from modules.infrastructure.services.admin_services import get_admins as core_get_admins
from modules.infrastructure.config.settings import Settings  
# Initialize settings
settings = Settings()


postgres_manager = PostgresManager(settings=settings)
db: Session = next(postgres_manager.get_db())

def login_admin(username: str = typer.Option(...), password: str = typer.Option(...)):
    admin_data = AdminLogins(username=username, password=password)
    response = core_get_admins(admin_data, db)
    typer.echo(f"Login successful. Token: {response['token']}")
