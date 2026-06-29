from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://uuekyfuechdvdyjbrvgo.supabase.co"
SUPABASE_KEY = "sb_secret_YrGaj6ltZkxb36aoqQSsEw_hSE0QPzS"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQLAlchemy compatibility stubs (for existing code that imports engine/Base)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Dummy SQLite engine (not used, but prevents import errors)
engine = create_engine("sqlite:///./mizu.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    return supabase
