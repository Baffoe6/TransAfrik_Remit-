"""Tests for database URL normalization."""

from app.utils.database_url import normalize_database_url


def test_postgres_scheme_normalized():
    url = "postgres://user:pass@containers.railway.app:5432/railway"
    assert normalize_database_url(url) == (
        "postgresql://user:pass@containers.railway.app:5432/railway?sslmode=require"
    )


def test_postgresql_scheme_unchanged_local():
    url = "postgresql://transafrik:secret@localhost:5432/transafrik"
    assert normalize_database_url(url) == url


def test_ssl_not_duplicated():
    url = "postgresql://user:pass@host:5432/db?sslmode=disable"
    assert normalize_database_url(url) == url
