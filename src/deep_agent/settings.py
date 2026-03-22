from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model: str = "anthropic:claude-sonnet-4-6"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.3
    use_sandbox: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
