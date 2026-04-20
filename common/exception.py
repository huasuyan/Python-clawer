from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from common.result import Result

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content=Result.fail(msg=str(exc))
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content=Result.fail(code=exc.status_code, msg=exc.detail)
    )