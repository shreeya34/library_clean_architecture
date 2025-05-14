from sqlalchemy.orm import Session
from modules.domain.repositories.admin.admin_repositories import IAdminRepository
from modules.interfaces.response.admin_response import (
    BookViewResponse,
    BookAvailabilityResponse,
)


def book_response(book) -> tuple:
    is_available = book.stock > 0
    response = (
        BookAvailabilityResponse(
            title=book.title, author=book.author, available=True
        )
        if is_available
        else None
    )
    return is_available, response


class ViewBooksUseCase:
    def __init__(self, admin_repo: IAdminRepository):
        self.admin_repo = admin_repo

    def execute(self, db: Session, title: str = "") -> dict:
        books = (
            self.admin_repo.get_books_by_title(db, title)
            if title
            else self.admin_repo.get_all_books(db)
        )

        if not books:
            return BookViewResponse(message="No books found", books=[]).dict()

        result = []

        for book in books:
            is_available, response = book_response(book)

            self.admin_repo.upsert_availability(db, book.id, book.title, is_available)

            if response:
                result.append(response)

        self.admin_repo.commit(db)

        return BookViewResponse(message="Books available", books=result).dict()
