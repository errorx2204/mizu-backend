import os
from supabase import create_client, Client
from dotenv import load_dotenv
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set!")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is not set!")

SUPABASE_URL = SUPABASE_URL.strip()
SUPABASE_KEY = SUPABASE_KEY.strip()

# Create client with retry logic
def create_supabase_client(max_retries=3):
    for attempt in range(max_retries):
        try:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Test the connection
            client.auth.get_session()
            print("? Supabase client connected successfully")
            return client
        except Exception as e:
            print(f"?? Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

supabase: Client = create_supabase_client()
