from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Arete EVE Navigator"
    API_VERSION: str = "0.1.0"

    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = BASE_DIR / "app" / "data"

    UNIVERSE_FILE: Path = DATA_DIR / "universe.json"
    RISK_CONFIG_FILE: Path = DATA_DIR / "risk_config.json"

    ZKILL_BASE_URL: str = "https://zkillboard.com/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
