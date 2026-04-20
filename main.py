from contextlib import asynccontextmanager
from http.client import HTTPException

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.result import Result
from config.settings import settings
# from controller.user_controller import router as user_router
from common.exception import global_exception_handler, http_exception_handler
from websocket.java_client import start_java_client,java_ws


# 全局生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服务启动时执行（替代原来的 startup 事件）
    print("FastAPI 服务启动中...")
    # 在这里启动连接Java的WebSocket客户端
    start_java_client()
    print("Java WebSocket 后台连接任务已启动")

    yield

    # 服务关闭时执行（可选，做资源释放）
    print("FastAPI 服务正在关闭，清理资源...")

# 初始化应用 = SpringApplication.run
app = FastAPI(
    title="Python后端服务",
    version="1.0",
    lifespan=lifespan
)

# 注册全局异常
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
# app.include_router(user_router)


# 根接口
@app.get("/")
async def root():
    msg = {"code":200,"msg":"python发送消息给java后端并转发vue"}
    await java_ws.send(msg)
    return Result.success(msg="FastAPI 服务运行正常，对接SpringBoot就绪")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=False  # 生产环境关闭热更
    )