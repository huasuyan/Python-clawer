import json
import logging

from fastapi import APIRouter, HTTPException, Depends

from common.none_state import CrawlerNoneTaskState, NONE_STATE_TEXT
from common.result import Result
from entity.crawler_model import CrawlerNone
from entity.crawler_request import CrawlerIntegrationRequest
from service.tianapi_crawler_service import TianApiCrawlerService
from config.settings import settings
from config.db import get_db
from sqlalchemy.orm import Session

from websocketClient.java_client import java_ws

router = APIRouter(prefix="/api/python/crawler", tags=["爬虫接口"])

# 创建服务实例
crawler_service = None


def get_crawler_service():
    """获取爬虫服务实例"""
    global crawler_service
    if crawler_service is None:
        if not settings.TIANAPI_KEY:
            logging.error("请配置天行数据API！")
            raise HTTPException(status_code=500, detail="天行数据API密钥未配置")
        crawler_service = TianApiCrawlerService(api_key=settings.TIANAPI_KEY)
    return crawler_service


@router.post("/runIntegration")
async def run_integration(request: CrawlerIntegrationRequest,db: Session = Depends(get_db)):
    """
    整合爬虫接口

    参数说明：
    - key_word: 检索关键词（必填）
    - sources: 数据源列表，可选值：['综合', '社会']（必填）
    - page: 获取多少页的内容（默认1）

    说明：
    - 固定num=50，每页最多返回50条数据
    - 当某页返回数量不足50条时，停止该数据源的后续查询
    - 支持同时查询多个数据源

    示例：
    {
        "crawler_id":1,
    }

    返回格式：
    {
        "code": 1,
        "msg": "success",
        "data": {
            "dataList": [...]
        }
    }
    """
    try:
        # 获取服务实例
        service = get_crawler_service()

        # 获取爬虫信息
        crawlerInfo = db.query(CrawlerNone).filter(CrawlerNone.crawler_id == request.crawler_id).first()
        if not crawlerInfo:
            return Result.error(msg="未找到对应手动检索任务！")

        if crawlerInfo.state != CrawlerNoneTaskState.CREATED :
            return Result.error(msg=f"手动检索任务状态错误：要求状态为{NONE_STATE_TEXT[CrawlerNoneTaskState.CREATED]},当前状态为：{NONE_STATE_TEXT[crawlerInfo.state]}！")

        # 读取参数
        params_dict = crawlerInfo.params
        sources = list(params_dict.get("sources"))
        page = int(params_dict.get("page"))

        # 设置爬取状态
        crawler_old_state = crawlerInfo.state
        crawlerInfo.state = CrawlerNoneTaskState.CRAWLING
        db.add(crawlerInfo)
        db.commit()

        # websocket给java发消息
        ws_msg = {
            "type": "crawler_none_state_change",
            "crawler_id": request.crawler_id,
            "crawler_name": crawlerInfo.crawler_name,
            "crawler_old_state": NONE_STATE_TEXT[crawler_old_state],
            "crawler_new_state": NONE_STATE_TEXT[CrawlerNoneTaskState.CRAWLING]
        }
        await java_ws.send(ws_msg)

        # 执行爬取
        news_list = service.crawl_integration(
            key_word=crawlerInfo.key_word,
            sources=sources,
            page=page
        )

        # 设置爬取状态
        crawler_old_state = CrawlerNoneTaskState.CRAWLING
        crawlerInfo.state = CrawlerNoneTaskState.CLEANING
        db.add(crawlerInfo)
        db.commit()

        # websocket给java发消息
        ws_msg = {
            "type": "crawler_none_state_change",
            "crawler_id": request.crawler_id,
            "crawler_name": crawlerInfo.crawler_name,
            "crawler_old_state": NONE_STATE_TEXT[crawler_old_state],
            "crawler_new_state": NONE_STATE_TEXT[CrawlerNoneTaskState.CLEANING]
        }
        await java_ws.send(ws_msg)

        # 转换为字典列表
        data_list = [news.model_dump() for news in news_list]

        # 返回结果
        return {
            "code": 1,
            "msg": "success",
            "data": {
                "dataList": data_list
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")


@router.get("/test")
async def test_crawler():
    """测试接口"""
    return {
        "code": 1,
        "msg": "爬虫服务运行正常",
        "data": {
            "supported_sources": ["综合", "社会"],
            "max_num_per_page": 50
        }
    }
