import typer
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import NewBooks
from modules.infrastructure.services.admin_services import AdminService  # FIXED import
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
    
    mock_user = {"username": "admin", "is_admin": True}  # Simulated admin user

    admin_service = AdminService()  # Create service instance
    admin_service.add_books(book_data, db, mock_user)  # Call method correctly

    typer.echo(f"Book '{title}' by {author} added successfully with {stock} in stock.")
