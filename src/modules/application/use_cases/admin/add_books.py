from sqlalchemy.orm import Session
from modules.infrastructure.database.utils import commit_and_refresh
from modules.infrastructure.database.models.admin import Book
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.interfaces.request.admin_request import NewBooks
from modules.interfaces.response.admin_response import (
    BookAddResponse,
    BookResponseModel,
)
import uuid


class AddBooksUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, newbook: NewBooks) -> dict:
        book = self.admin_repo.get_existing_book(db, newbook)
        if book:
            book.stock += newbook.stock
            book.available = book.stock > 0
            self.admin_repo.commit(db)
            message = "Book updated successfully"
        else:
            book = Book(
                id=str(uuid.uuid4()),
                title=newbook.title,
                author=newbook.author,
                stock=newbook.stock,
                available=True,
            )
            commit_and_refresh(db, book)
            message = "Book added successfully"

        return BookAddResponse(
            message=message, new_book=BookResponseModel.from_orm(book)
        ).dict()
