import uuid
from modules.domain.exceptions.member.exception import InvalidUUIDError


def parse_uuid(id_str: str) -> uuid.UUID:
    try:
        return uuid.UUID(id_str)
    except ValueError:
        raise InvalidUUIDError()
