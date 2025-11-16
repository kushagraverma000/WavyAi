from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration.

    Uses environment variables where possible. Defaults are chosen so the
    backend can run out-of-the-box with a local SQLite database, while allowing
    seamless switch to PostgreSQL by setting DATABASE_URL.
    """

    # Database
    database_url: str = Field(
        default="sqlite:///./wavyai.db",
        description="SQLAlchemy connection string. Override with a PostgreSQL URL in production.",
        env="DATABASE_URL",
    )

    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    raw_data_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "raw")
    vectorstore_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "vectorstore")

    # Runtime mode: 'light' (no heavy deps) or 'full' (scientific + LLM stack)
    mode: str = Field(
        default="light",
        description="Operation mode: 'light' (default) or 'full' for ARGO+LLM backend.",
        env="WAVYAI_MODE",
    )

    # AI / Gemini
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key", env="GOOGLE_API_KEY")
    gemini_chat_model: str = "gemini-1.5-pro"
    gemini_embedding_model: str = "models/embedding-001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
