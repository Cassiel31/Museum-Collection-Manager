
from pathlib import Path
from dotenv import dotenv_values
from supabase import create_client, Client

# Locate .env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Read credentials directly from .env
config = dotenv_values(ENV_PATH)

SUPABASE_URL = "https://ainbluxcozfpnlvxikfb.supabase.co"
SUPABASE_KEY = config.get("SUPABASE_KEY")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing or empty in .env")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Supabase client created successfully!")
