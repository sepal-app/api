import contextvars
import types

# A global context for storing per request variables
_request_global = contextvars.ContextVar(
    "request_global", default=types.SimpleNamespace()
)


def init(data):
    _request_global.set(data)


def request_global():
    return _request_global.get()
