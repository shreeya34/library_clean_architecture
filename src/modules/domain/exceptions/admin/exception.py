from modules.domain.exceptions.base import LibraryHTTPException


class AdminAlreadyExistsError(LibraryHTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=400, detail=f"Admin with the name '{name}' already exists!"
        )


class InvalidAdminCredentialsError(LibraryHTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=401, detail=f"Invalid credentials for admin '{name}'"
        )


class MemberAlreadyExistsError(LibraryHTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=400, detail=f"Member with the name '{name}' already exists!"
        )


class MemberNotFoundError(LibraryHTTPException):
    def __init__(self, member_id: str):
        super().__init__(
            status_code=400, detail=f"Member with ID '{member_id}' not found!"
        )


class BookUnavailableError(LibraryHTTPException):
    def __init__(self, title: str):
        super().__init__(
            status_code=404,
            detail=f"Book with title '{title}' is currently unavailable!",
        )


class BookNotFoundError(LibraryHTTPException):
    def __init__(self, title: str):
        super().__init__(
            status_code=404, detail=f"Book with title '{title}' not found!"
        )


class AdminAccessDeniedError(LibraryHTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")
