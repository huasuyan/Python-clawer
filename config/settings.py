from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 服务配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8088
    # 跨域配置
    CORS_ORIGINS: str = "*"
    # websocket服务器地址
    WEBSOCKET_SERVER: str = "ws://localhost:8080/ws/python"
    # Mysql
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # 天行数据API配置
    TIANAPI_KEY: str = ""  # 天行数据API密钥

    # 通义千问API配置
    QWEN_API_KEY: str = ""  # 通义千问API密钥

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """动态构建数据库连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# 初始化配置
settings = Settings()