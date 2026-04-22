from supabase import create_client, Client
from config import settings
from fastapi import HTTPException

_client: Client | None = None


def get_db() -> Client:
    global _client
    if _client is None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise HTTPException(500, "Supabase not configured — set SUPABASE_URL and SUPABASE_SERVICE_KEY in Vercel environment variables")
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client
