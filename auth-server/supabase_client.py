import os
from dotenv import load_dotenv

from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise ValueError("Missing SUPABASE_URL")

if not SUPABASE_ANON_KEY:
    raise ValueError("Missing SUPABASE_KEY")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing SUPABASE_SERVICE_ROLE_KEY")

admin_client: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

auth_client: Client = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
)