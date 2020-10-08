from typing import Any, Dict

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    TESTING_ENV: bool = False
    PROJECT_NAME: str = "Async OAuth2 Provider"

    OAUTH2_CLIENT_ID: str = "67IGqEoQ8ddoh5s0wuJll51G"
    OAUTH2_CLIENT_SECRET: str = "h4s5RJ4OMu92jk0e5scodq5nNPhblW"
    OAUTH2_USERNAME: str = "admin"
    OAUTH2_PASSWORD: str = "admin"
    # NOTE: Remove. Dynamically build redirect uri
    OAUTH2_REDIRECT_URI: AnyHttpUrl

    DB_DSN: str

    @validator("DB_DSN", pre=True)
    def assemble_db_connection(cls, v: str, values: Dict[str, Any]) -> Any:
        if values.get("TESTING_ENV"):
            return f"{v}_test"

        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
