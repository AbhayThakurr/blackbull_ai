from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    DATABASE_URL: str
    DISCORD_BOT_TOKEN: str
    HF_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore[call-arg]
