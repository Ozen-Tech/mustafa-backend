from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    GOOGLE_API_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 dias

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.env"), 
        env_file_encoding='utf-8',
        extra='ignore'  # Ignora campos extras no .env
    )

settings = Settings()