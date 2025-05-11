import click
from sqlalchemy.orm import Session
from entrypoints.cli.db_utils import get_db
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.infrastructure.repositories.admin.admin_repositories_impl import AdminRepository
from modules.interfaces.request.admin_request import NewBooks
from modules.application.services.admin_services import AdminService
from modules.infrastructure.config.settings import Settings


@click.command()
@click.option("--title", prompt="Book title", help="Book title")
@click.option("--author", prompt="Book author", help="Book author")
@click.option(
    "--stock",
    prompt="Number of copies available",
    type=int,
    help="Number of copies available",
)
def add_book(title: str, author: str, stock: int):
    """
    Add a new book to the system.
    """

    db = get_db()
    book_data = NewBooks(title=title, author=author, stock=stock)
    admin_repo = AdminRepository() 
    admin_service = AdminService(admin_repo)

    mock_user = {"username": "admin", "is_admin": True}
    admin_service.add_books(book_data, db, mock_user)

    click.echo(f"Book '{title}' by {author} added successfully with {stock} in stock.")


if __name__ == "__main__":
    add_book()
