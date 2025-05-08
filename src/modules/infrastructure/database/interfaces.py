from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker, Session


class DatabaseManager(ABC):
    @abstractmethod
    def get_engine(self):
        pass

    @abstractmethod
    def get_session(self) -> Session:
        pass

    @abstractmethod
    def init_db(self):
        pass
