from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        try:
            response = await call_next(request)
            return response

        except Exception:
            raise 