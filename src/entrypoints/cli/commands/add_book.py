import click
from entrypoints.cli.db_utils import get_db
from modules.application.use_cases.admin.add_books import AddBooksUseCase
from modules.infrastructure.repositories.admin.admin_repositories_impl import (
    AdminRepository,
)
from entrypoints.api.admin.request import NewBooks
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
    add_books_usecase = AddBooksUseCase(admin_repo)

    result = add_books_usecase.add_or_update_book(db, book_data)

    click.echo(result["message"])
    click.echo(
        f"Book '{result['new_book']['title']}' by {result['new_book']['author']} "
        f"now has {result['new_book']['stock']} in stock."
    )


if __name__ == "__main__":
    add_book()