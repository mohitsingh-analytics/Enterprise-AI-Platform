from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        print("Request received")
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        print(f"Request ID: {request_id}")
        response = await call_next(request)
        print("Response returned")

        return response