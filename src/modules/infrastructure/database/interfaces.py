from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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