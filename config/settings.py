from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 服务配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8088
    # 跨域配置（修复版，自动解析逗号分隔字符串）
    CORS_ORIGINS: str = "*"
    # websocket服务器地址
    WEBSOCKET_SERVER = "ws://localhost:8080/ws/python"
    # Mysql
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "你的密码"
    DB_NAME = "你的数据库名"
    # 数据库连接地址
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# 初始化配置
settings = Settings()