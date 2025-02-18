import secrets

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Twitter NG trends"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Retrieves the 5 latest tweets from the top 10 trending tweets on Twitter Ng"
    API_PREFIX: str = ""
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEBUG: bool = False
    TESTING: bool = False


settings = Settings()
