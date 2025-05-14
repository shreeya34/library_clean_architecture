from typing import Optional
from sqlalchemy.orm import Session
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Book
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.interfaces.request.admin_request import NewBooks
from modules.interfaces.response.admin_response import BookAddResponse, BookResponseModel
import uuid


def create_new_book(newbook: NewBooks) -> Book:
    return Book(
        id=str(uuid.uuid4()),
        title=newbook.title,
        author=newbook.author,
        stock=newbook.stock,
        available=True,
    )

def update_existing_book(book: Book, additional_stock: int) -> Book:
    book.stock += additional_stock
    book.available = book.stock > 0
    return book


class AddBooksUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, newbook: NewBooks) -> dict:
        existing_book: Optional[Book] = self.admin_repo.get_existing_book(db, newbook)

        if existing_book:
            updated_book = update_existing_book(existing_book, newbook.stock)
            self.admin_repo.commit(db)
            message = "Book updated successfully"
        else:
            updated_book = create_new_book(newbook)
            commit_and_refresh(db, updated_book)
            message = "Book added successfully"

        return BookAddResponse(
            message=message, new_book=BookResponseModel.from_orm(updated_book)
        ).dict()
