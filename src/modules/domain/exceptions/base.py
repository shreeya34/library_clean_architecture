
from abc import ABC, abstractmethod
from fastapi import HTTPException

class LibraryHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)
