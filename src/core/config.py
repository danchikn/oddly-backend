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

    RABBITMQ_URL: str = 'amqp://guest:guest@localhost:5672/'

    SMTP_HOST: str = 'smtp.gmail.com'
    SMTP_PORT: int = 587
    SMTP_USER: str = ''
    SMTP_PASSWORD: str = ''
    SMTP_FROM: str = ''

    REDIS_URL: str = 'redis://localhost:6379/0'
    VERIFY_CODE_TTL: int = 600  # 10 minutes

    STRIPE_SECRET_KEY: str = ''
    FRONTEND_URL: str = 'http://localhost:3000'

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()
