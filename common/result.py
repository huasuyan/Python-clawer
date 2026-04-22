from typing import Any

class Result:
    @staticmethod
    def success(data: Any = None, msg: str = "success") -> dict:
        return {
            "code": 1,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def successDataList(dataList: Any = None, msg: str = "success") -> dict:
        return {
            "code": 1,
            "msg": msg,
            "data": {
                "dataList": dataList
            }
        }

    @staticmethod
    def error(msg: str = "error", data: Any = None, code: int = 0) -> dict:
        return {
            "code": code,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def fail(code: int = 0, msg: str = "fail", data: Any = None) -> dict:
        """兼容旧方法"""
        return Result.error(msg=msg, data=data, code=code)