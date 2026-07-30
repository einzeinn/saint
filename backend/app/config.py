from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    app_name: str = "Saint"
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"

    frontend_origin: str = "http://localhost:5173"

    llm_provider: str = "mock"
    llm_model: str = "mock-context-guide"
    llm_api_key: str = ""
    llm_base_url: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    groq_base_url: str = ""
    llm_model: str = ""  # used specifically for Gemini
    groq_model: str = ""  # used specifically for Groq

    datahub_provider: str = "mock"
    datahub_gms_url: str = "http://localhost:8080"
    datahub_gms_token: str = Field(default="", repr=False)
    datahub_mcp_url: str = ""
    datahub_mcp_timeout_seconds: float = 10
    datahub_token: str = Field(default="", repr=False)
    datahub_mcp_search_tool: str = "search"
    datahub_mcp_entity_tool: str = "get_entities"
    datahub_mcp_command: str = "uvx"
    datahub_mcp_args: str = "mcp-server-datahub@latest"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
