"""Database checks. Run in CI against the pgvector service; skipped when DATABASE_URL is unset."""

import os

import psycopg
import pytest

DATABASE_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not set")


def test_pgvector_extension_available():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        row = conn.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector").fetchone()
    assert row is not None
    assert row[0] == pytest.approx(1.0)
