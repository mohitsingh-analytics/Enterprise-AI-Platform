from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        try:
            request.state.request_id = str(uuid.uuid4())
            response = await call_next(request)
            return response

        except Exception:
            raise 