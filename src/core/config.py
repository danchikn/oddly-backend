from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://postgres:postgres@localhost:5432/oddly'
    JWT_SECRET: str = 'super-secret-change-me'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    S3_ENDPOINT_URL: str = ''
    S3_ACCESS_KEY: str = ''
    S3_SECRET_KEY: str = ''
    S3_BUCKET: str = ''
    S3_REGION: str = 'us-east-1'
    S3_PUBLIC_URL: str = ''

    UPLOAD_MAX_SIZE: int = 5 * 1024 * 1024  # 5 MB
    UPLOAD_ALLOWED_TYPES: list[str] = ['image/jpeg', 'image/png', 'image/webp']

    class Config:
        env_file = '.env'


settings = Settings()
