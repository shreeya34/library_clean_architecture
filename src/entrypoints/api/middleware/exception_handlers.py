from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from modules.domain.exceptions.member.exception import RaiseUnauthorizedError
from modules.infrastructure.logger import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except RequestValidationError as val_err:
            logger.warning(f"Validation Error: {val_err.errors()}")
            return JSONResponse(
                status_code=422,
                content={"detail": val_err.errors()},
            )
        except RaiseUnauthorizedError as auth_err:
            logger.warning(f"Unauthorized Access: {str(auth_err)}")
            return JSONResponse(
                status_code=401,
                content={"detail": str(auth_err)},
            )

        except Exception as exc:
            logger.error(f"Internal Server Error: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500, content={"detail": "An unexcepted error occurred."}
            )
