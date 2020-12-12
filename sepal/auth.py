from firebase_admin.auth import verify_id_token
from fastapi import Depends, Header, HTTPException

from sepal.settings import settings


class AuthError(HTTPException):
    def __init__(self, code, description, status_code=401):
        detail = {"code": code, "description": description}
        super().__init__(
            status_code, detail=detail, headers={"content-type": "application/json"}
        )


def get_auth_header_token(auth: str = Header(None, alias="authorization")):
    """Return the access token from the authorization header."""
    if not auth:
        raise AuthError(
            code="authorization_header_missing",
            description="Authorization header is expected",
        )

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            code="invalid_header",
            description='Authorization header must start with "Bearer"',
        )
    elif len(parts) == 1:
        raise AuthError(code="invalid_header", description="Token not found")
    elif len(parts) > 2:
        raise AuthError(
            code="invalid_header",
            description="Authorization header must be" " Bearer token",
        )
    token = parts[1]
    return token


def decode_token(token: str = Depends(get_auth_header_token)):
    return verify_id_token(token)


def get_current_user(payload=Depends(decode_token)) -> str:
    """Return the id of the user"""
    return payload.get("sub", None)
