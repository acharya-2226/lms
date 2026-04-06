import uuid

from LMS.logging_utils import request_id_context


class RequestIDMiddleware:
    """Attach a correlation id to every request and response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        token = request_id_context.set(request_id)
        request.request_id = request_id
        try:
            response = self.get_response(request)
        finally:
            request_id_context.reset(token)

        response['X-Request-ID'] = request_id
        return response
