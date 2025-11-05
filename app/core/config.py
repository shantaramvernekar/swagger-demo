from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Swagger Demo with FastAPI"
    version: str = "1.0.0"
    api_key_header_name: str = "X-API-Key"
    API_KEY: str = "secret123"


settings = Settings()

