from functools import lru_cache
from typing import Any, Dict, List
from urllib.request import urlopen

import orjson as json
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt

from sepal.settings import settings


class AuthError(HTTPException):
    def __init__(self, code, description, status_code=401):
        detail = {"code": code, "description": description}
        super().__init__(
            status_code, detail=detail, headers={"content-type": "application/json"}
        )


def get_auth_header_token(auth: str = Header(None, alias="authorization")):
    """Obtains the Access Token from the Authorization Header
    """
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


@lru_cache
def get_jwks(domain: str):
    jsonurl = urlopen("https://" + domain + "/.well-known/jwks.json")
    return json.loads(jsonurl.read())


def decode_token(token: str = Depends(get_auth_header_token)):
    jwks = get_jwks(settings.auth0_domain)
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if not rsa_key:
        raise AuthError(
            code="invalid_header", description="Unable to find appropriate key",
        )

    try:
        return jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.token_algorithm],
            audience=settings.token_audience,
            issuer="https://" + settings.auth0_domain + "/",
        )
    except jwt.ExpiredSignatureError:
        raise AuthError(code="token_expired", description="token is expired")
    except jwt.JWTClaimsError:
        raise AuthError(
            code="invalid_claims",
            description="incorrect claims, please check the audience and issuer",
        )
    except Exception:
        raise AuthError(
            code="invalid_header", description="Unable to parse authentication token.",
        )


def require_scopes(required_scopes: List[str]):
    def _inner(payload: Dict[str, any] = Depends(decode_token)):
        scopes = payload.get("scope", "")
        if not scopes or len(scopes) == 0:
            raise AuthError(
                code="invalid_scopes", description="The token scope is invalid"
            )

        scopes = scopes.split(" ")
        for scope in required_scopes:
            if scope not in scopes:
                raise AuthError(
                    code="missing_scopes",
                    description=f'The auth token does not include the "{scope}" scope is invalid',
                )

        return scopes

    return _inner
