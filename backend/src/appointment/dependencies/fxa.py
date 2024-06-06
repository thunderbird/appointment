import logging
import os
import datetime

from fastapi import Request, Depends

# from jose import jwt, jwk
import jwt

from ..controller.apis.fxa_client import FxaClient


def get_fxa_client():
    """Returns an instance of FxaClient. Don't forget to run setup!"""
    return FxaClient(os.getenv("FXA_CLIENT_ID"), os.getenv("FXA_SECRET"), os.getenv("FXA_CALLBACK"))


def get_webhook_auth(request: Request, fxa_client: FxaClient = Depends(get_fxa_client)):
    """Handles decoding and verification of an incoming SET (See: https://mozilla.github.io/ecosystem-platform/relying-parties/tutorials/integration-with-fxa#webhook-events)"""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        logging.error("FXA webhook event with no authorization.")
        return None

    header_type, header_token = auth_header.split(" ")
    if header_type != "Bearer":
        logging.error(f"Error decoding token. Type == {header_type}, which is not Bearer!")
        return None

    fxa_client.setup()
    public_jwks = fxa_client.get_jwk()

    if not public_jwks:
        logging.error("No public jwks available.")
        return None

    headers = jwt.get_unverified_header(header_token)

    if "kid" not in headers:
        logging.error("Error decoding token. Key ID is missing from headers.")
        return None

    jwk_pem = None
    for current_jwk in public_jwks:
        if current_jwk.get("kid") == headers.get("kid"):
            jwk_pem = jwt.PyJWK(current_jwk).key
            break

    if jwk_pem is None:
        logging.error(f"Error decoding token. Key ID ({headers.get('kid')}) is missing from public list.")
        return None

    # Amount of time over what the iat is issued for to allow
    # We were having millisecond timing issues, so this is set to a few seconds to cover for that.
    leeway = datetime.timedelta(seconds=5)
    decoded_jwt = jwt.decode(
        header_token, key=jwk_pem, audience=fxa_client.client_id, algorithms="RS256", leeway=leeway
    )

    # Final verification
    if decoded_jwt.get("iss") != fxa_client.config.issuer:
        logging.error(f"Issuer is not valid: ({decoded_jwt.get('iss')}) vs ({fxa_client.config.issuer})")

    return decoded_jwt
