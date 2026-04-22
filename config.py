from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Dripify login (only needed for local sync, optional on Vercel)
    dripify_email: str = ""
    dripify_password: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_assistant_id: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # Agent
    poll_interval_minutes: int = 10
    log_level: str = "INFO"


settings = Settings()
