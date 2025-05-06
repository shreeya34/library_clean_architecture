import typer
from sqlalchemy.orm import Session

from modules.domain.member.models import MemberLogins
from modules.infrastructure.config.config import Settings
from modules.infrastructure.services.member_services import member_logins
from modules.infrastructure.database.postgres_manager import PostgresManager

settings = Settings()


postgres_manager = PostgresManager(settings=settings)
db: Session = next(postgres_manager.get_db())

def member_login(name: str = typer.Option(..., help="Member name")):
    login_data = MemberLogins(name=name)
    db = next(postgres_manager.get_db())

    try:
        result = member_logins(memberLogin=login_data, db=db)
        typer.echo(f"{result['message']}")
        typer.echo(f"Member ID: {result['member_id']}")
    except Exception as e:
        typer.echo(f"Login failed: {e}")
