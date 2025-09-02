from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
	database_url: str = "postgresql+psycopg2://crosscoach:crosscoach@db:5432/crosscoach"
	backend_host: str = "0.0.0.0"
	backend_port: int = 8000
	cors_origins: str = "http://localhost:5173"
	openai_api_key: str = ""
	openai_api_base: str = "https://api.openai.com/v1"
	openai_model: str = "gpt-4o-mini"
	
	# JWT Settings
	secret_key: str = secrets.token_urlsafe(32)
	algorithm: str = "HS256"
	access_token_expire_minutes: int = 30

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

settings = Settings() 