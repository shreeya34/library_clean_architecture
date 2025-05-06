import typer
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import AdminLogins
from modules.infrastructure.services.admin_services import get_admins
from modules.infrastructure.services.admin_services import view_available_books as core_view_books
from modules.infrastructure.config.settings import Settings  
settings = Settings()


postgres_manager = PostgresManager(settings=settings)
db: Session = next(postgres_manager.get_db())


def view_books(
    admin_username: str = typer.Option(..., help="Admin username"),
    admin_password: str = typer.Option(..., help="Admin password"),
    title: str = typer.Option("", help="Search by book title (optional)"),
    status: str = typer.Option("active") 
):
    admin_data = AdminLogins(username=admin_username, password=admin_password)
    admin_response = get_admins(admin_data, db)
    
    user = {
        "username": admin_username,
        "admin_id": admin_response["admin_id"],
        "is_admin": True 
    }

    result = core_view_books(title=title, db=db, user=user)

    if not result.get("books", []):
        typer.echo(result["message"])
    else:
        typer.echo(result["message"])
        for book in result["books"]:
            typer.echo(f"Title: {book['title']} | Author: {book['author']} | Available: {book['available']}")