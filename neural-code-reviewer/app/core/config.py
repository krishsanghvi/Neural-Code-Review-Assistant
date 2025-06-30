import os
from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    # GitHub App settings
    github_app_id: int = 0
    github_private_key_path: str = "private-key.pem"
    github_webhook_secret: str = ""

    # Support private key as environment variable (for production)
    github_private_key_content: str = ""

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", 8000))  # Railway uses PORT env var
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def github_private_key(self) -> str:
        """Read the GitHub private key from file or environment"""
        # First try environment variable (for production)
        if self.github_private_key_content:
            return self.github_private_key_content

        # Fallback to file (for local development)
        key_path = Path(self.github_private_key_path)
        if key_path.exists():
            return key_path.read_text()
        return ""


# Global settings instance
settings = Settings()
