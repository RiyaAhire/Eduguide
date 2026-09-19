"""Fail clearly when the configured Django database cannot be reached."""

import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from django.db import connection

try:
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
except Exception as error:
    print(f"Database connection failed: {error}", file=sys.stderr)
    sys.exit(1)

print(f"Database connection successful ({connection.vendor}).")
