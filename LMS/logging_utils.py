from contextvars import ContextVar


request_id_context = ContextVar('request_id', default='-')


class RequestIDFilter:
    def filter(self, record):
        record.request_id = request_id_context.get('-')
        return True
