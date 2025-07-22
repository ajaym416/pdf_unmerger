from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"
    broker_url: str = redis_url
    result_backend: str = redis_url
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "pdf-splits"
    gemini_api_key: str = "your-gemini-api-key"

    class Config:
        env_file = ".env"

settings = Settings()