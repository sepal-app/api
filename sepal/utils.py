from base64 import b64encode
from urllib.parse import urljoin


def make_cursor_link(request_url: str, cursor: str, limit: int):
    encoded_cursor = b64encode(cursor.encode()).decode()
    return urljoin(str(request_url), f"?limit={limit}&cursor={encoded_cursor}")
