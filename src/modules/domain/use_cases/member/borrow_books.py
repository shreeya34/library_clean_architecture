
from modules.domain.exceptions.admin.exception import BookUnavailableError, MemberNotFoundError
from modules.domain.exceptions.member.exception import DuplicateBookBorrowError, OnlyMembersCanBorrowError
from modules.domain.repositories.member.member_repositories import IMemberRepository
from modules.interfaces.request.member_request import BorrowBookRequest
from modules.interfaces.response.member_response import BorrowedBookResponse
from modules.shared.utils.member_utils import create_borrowed_book_entry, parse_uuid
from sqlalchemy.orm import Session


class BorrowBookUseCase:
    def __init__(self, member_repo: IMemberRepository):
        self.member_repo = member_repo

    def execute(self, book_request: BorrowBookRequest, db: Session, current_user: dict) -> BorrowedBookResponse:
        if current_user.get("is_admin"):
            raise OnlyMembersCanBorrowError()

        member_id = str(parse_uuid(current_user.get("admin_id", "")))
        member = self.member_repo.get_member_by_id(db, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        books = self.member_repo.get_available_books_by_title(db, book_request.book_title)
        if not books:
            raise BookUnavailableError(book_request.book_title)

        book = books[0]
        if self.member_repo.has_already_borrowed(db, book.id, member.member_id):
            raise DuplicateBookBorrowError(book.title)

        borrowed = create_borrowed_book_entry(book, member)
        book.stock -= 1
        self.member_repo.save_borrowed_book(db, borrowed)

        return BorrowedBookResponse(
            title=borrowed.title,
            member_id=borrowed.member_id,
            name=borrowed.name,
            borrow_date=borrowed.borrow_date,
            expiry_date=borrowed.expiry_date,
        )