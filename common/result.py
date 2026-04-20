from typing import Any

class Result:
    @staticmethod
    def success(data: Any = None, msg: str = "success") -> Any:
        return {
            "code": 1,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def fail(code: int = 0, msg: str = "fail", data: Any = None):
        return {
            "code": code,
            "msg": msg,
            "data": data
        }