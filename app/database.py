from pathlib import Path
from dotenv import dotenv_values
from supabase import create_client, Client

# Locate .env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Read credentials
config = dotenv_values(ENV_PATH)

SUPABASE_URL = config.get("SUPABASE_URL")
SUPABASE_KEY = config.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or key is missing from .env")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Supabase client created successfully!")