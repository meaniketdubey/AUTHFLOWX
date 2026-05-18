from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        extra = "ignore" 



settings = Settings()