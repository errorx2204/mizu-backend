import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate env vars with clear error messages
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set!")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is not set!")

# Strip any accidental whitespace
SUPABASE_URL = SUPABASE_URL.strip()
SUPABASE_KEY = SUPABASE_KEY.strip()

print(f"DEBUG: SUPABASE_URL = {SUPABASE_URL}")
print(f"DEBUG: SUPABASE_KEY starts with = {SUPABASE_KEY[:20]}...")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
