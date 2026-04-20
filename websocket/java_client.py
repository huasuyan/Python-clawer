import asyncio
import websockets
import json
from typing import Optional, Dict, Any

class JavaWebSocketClient:
    _instance: Optional["JavaWebSocketClient"] = None
    _websocket: Optional[websockets.WebSocketClientProtocol] = None
    _connected: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.JAVA_WS_URL = "ws://localhost:8080/ws/python"

    # 启动后台连接（项目启动时调用）
    async def start(self):
        while True:
            try:
                async with websockets.connect(self.JAVA_WS_URL) as websocket:
                    self._websocket = websocket
                    self._connected = True
                    print("✅ 已连接 Java WebSocket")

                    # 上线通知
                    await self.send({
                        "type": "python_connect",
                        "msg": "Python 服务已上线"
                    })

                    # 监听消息
                    async for message in websocket:
                        await self._on_message(message)

            except Exception as e:
                self._connected = False
                self._websocket = None
                print(f"❌ 连接断开，5秒后重连: {e}")
                await asyncio.sleep(5)

    # 收到消息处理
    async def _on_message(self, message: str):
        print(f"📩 收到 Java 指令：{message}")
        try:
            data = json.loads(message)
            # 你可以在这里写业务逻辑
        except:
            print("⚠️ 非JSON消息")

    # =========================================
    # 🔥 手动发消息给 Java（全局随便调用）
    # =========================================
    async def send(self, data: Dict[str, Any]):
        if not self._connected or not self._websocket:
            print("⚠️ 未连接，无法发送")
            return

        try:
            msg = json.dumps(data, ensure_ascii=False)
            await self._websocket.send(msg)
            print(f"📤 已发送到 Java：{msg}")
        except Exception as e:
            print(f"发送失败：{e}")

    def is_connected(self):
        return self._connected

# 全局单例
java_ws = JavaWebSocketClient()

# 项目启动入口
def start_java_client():
    asyncio.create_task(java_ws.start())