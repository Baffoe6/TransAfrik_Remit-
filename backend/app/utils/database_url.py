"""Normalize database URLs for cloud providers (Railway, Heroku, etc.)."""


def normalize_database_url(url: str) -> str:
    if not url:
        return url

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    is_local = any(host in url for host in ("localhost", "127.0.0.1", "@db:"))
    if not is_local and "sslmode=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"

    return url
