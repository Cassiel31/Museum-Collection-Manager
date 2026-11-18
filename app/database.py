"""Supabase connection configuration.

The web application can start without local credentials so routes and templates can
be inspected. Database-backed requests fail with a clear configuration message until
SUPABASE_URL and SUPABASE_KEY are supplied in the project-root .env file.
"""
from pathlib import Path
from dotenv import dotenv_values

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
config = dotenv_values(ENV_PATH)
SUPABASE_URL = config.get("SUPABASE_URL")
SUPABASE_KEY = config.get("SUPABASE_KEY")

class _UnavailableSupabase:
    def table(self, _name):
        raise RuntimeError("Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY to the project-root .env file.")

if SUPABASE_URL and SUPABASE_KEY:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = _UnavailableSupabase()
