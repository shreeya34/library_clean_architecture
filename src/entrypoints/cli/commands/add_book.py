from fastapi import Request
import typer
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import NewBooks
from modules.infrastructure.services.admin_services import add_user_books as core_add_book
from modules.infrastructure.config.settings import Settings  
settings = Settings()


postgres_manager = PostgresManager(settings=settings)
db: Session = next(postgres_manager.get_db())

def add_book(
    title: str = typer.Option(..., help="Book title"),
    author: str = typer.Option(..., help="Book author"),
    stock: int = typer.Option(..., help="Number of copies available")
):
    book_data = NewBooks(title=title, author=author, stock=stock)
    fake_request = Request(scope={"type": "http"})  # Dummy request object
    mock_user = {"username": "admin", "is_admin": True}
    core_add_book(fake_request, book_data, db, mock_user)
    typer.echo(f"Book '{title}' by {author} added successfully with {stock} in stock.")

