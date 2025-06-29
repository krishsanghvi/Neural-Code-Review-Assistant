import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # GitHub App settings
    github_app_id: int = 0
    github_private_key_path: str = "private-key.pem"
    github_webhook_secret: str = ""

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def github_private_key(self) -> str:
        """Read the GitHub private key from file"""
        key_path = Path(self.github_private_key_path)
        if key_path.exists():
            return key_path.read_text()
        return ""


# Global settings instance
settings = Settings()
