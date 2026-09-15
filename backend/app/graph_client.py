"""Microsoft Graph client: MSAL device-code auth (delegated Mail.Send /
Mail.Read) against the operator's own mailbox.

Scaffold only for now - token cache plumbing is in place, but the actual
device-code acquisition, send_mail, and reply-lookup calls are a TODO that
lands in a follow-up commit once there's a real Azure App Registration to
test against.
"""

import atexit
import os
from datetime import datetime

import msal

from config import Config

GRAPH_SCOPES = ["Mail.Send", "Mail.Read"]
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def _load_token_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if os.path.exists(Config.TOKEN_CACHE_PATH):
        with open(Config.TOKEN_CACHE_PATH, "r") as f:
            cache.deserialize(f.read())

    atexit.register(lambda: _persist_token_cache(cache))
    return cache


def _persist_token_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        with open(Config.TOKEN_CACHE_PATH, "w") as f:
            f.write(cache.serialize())


def _build_app() -> msal.PublicClientApplication:
    return msal.PublicClientApplication(
        client_id=Config.AZURE_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{Config.AZURE_TENANT_ID}",
        token_cache=_load_token_cache(),
    )


def get_access_token() -> str:
    """Acquire a Graph access token silently from the cache, falling back to
    an interactive device-code sign-in on first run.

    TODO (follow-up commit): implement silent-then-device-code acquisition.
    """
    raise NotImplementedError


def send_mail(to_email: str, subject: str, html_body: str) -> None:
    """Send a message as the signed-in operator via Graph's /me/sendMail.

    TODO (follow-up commit): implement.
    """
    raise NotImplementedError


def has_reply_since(from_addresses: list[str], since: datetime) -> bool:
    """Check the operator's Inbox for any message from one of
    `from_addresses` received after `since`.

    TODO (follow-up commit): implement.
    """
    raise NotImplementedError
