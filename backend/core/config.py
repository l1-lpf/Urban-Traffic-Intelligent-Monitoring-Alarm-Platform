from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Urban Traffic AI Platform"

    # MySQL 配置
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "33669900"
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = "urban_traffic_db"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # JWT 配置
    SECRET_KEY: str = "my-super-secret-urban-traffic-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天过期


settings = Settings()
