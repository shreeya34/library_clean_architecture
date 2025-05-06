import typer
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import NewMember
from modules.infrastructure.services.admin_services import get_member as core_get_member
from modules.infrastructure.config.settings import Settings

# Setup DB connection
settings = Settings()
postgres_manager = PostgresManager(settings=settings)
db = next(postgres_manager.get_db())

def add_member(
    name: str = typer.Option(..., help="Member name"),
    role: str = typer.Option(..., help="Member role")
):
    new_member = NewMember(name=name, role=role)

    user = {"is_admin": True}

    response = core_get_member(request=new_member, newuser=new_member, db=db, user=user)
    typer.echo(f"New member '{name}' added successfully with role '{role}'.")
