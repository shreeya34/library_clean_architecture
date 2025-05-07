

from modules.domain.exceptions.base import LibraryHTTPException 


class AdminAccessDeniedError(LibraryHTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")

class InvalidMemberCredentialsError(LibraryHTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=401,
            detail=f"Invalid credentials for member '{name}'"
        )


class RaiseUnauthorizedError(LibraryHTTPException):
    def __init__(self):
       
        super().__init__(status_code=401, detail="User not authenticated")


class RaiseBookError(LibraryHTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Unable to return the book")


class RaiseBorrowBookError(LibraryHTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Unable to borrow the book")


class DuplicateBookBorrowError(LibraryHTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=400,
            detail=f"Book '{book_title}' has already been borrowed by you."
        )


class BookNotBorrowedError(LibraryHTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=400,
            detail=f"The book '{book_title}' was not borrowed by the member."
        )


class BookAlreadyReturnedError(LibraryHTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=400,
            detail=f"Book '{book_title}' was already returned"
        )
