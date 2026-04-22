import json
import logging

from fastapi import APIRouter, HTTPException, Depends

from common.crawler_state import CrawlerNoneTaskState, NONE_STATE_TEXT, CrawlerCronTaskState, CRON_STATE_TEXT
from common.result import Result
from entity.crawler_model import CrawlerNone, CrawlerCron
from entity.crawler_request import CrawlerIntegrationRequest
from service.tianapi_crawler_service import TianApiCrawlerService
from config.settings import settings
from config.db import get_db
from sqlalchemy.orm import Session

from utils.tools import merge_unique_news, list_intersect
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

        if request.crawler_way == "none":
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
                "user_id": crawlerInfo.user_id,
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
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.crawler_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": NONE_STATE_TEXT[crawler_old_state],
                "crawler_new_state": NONE_STATE_TEXT[CrawlerNoneTaskState.CLEANING]
            }
            await java_ws.send(ws_msg)

            # 转换为字典列表
            data_list = [news.model_dump() for news in news_list]

            # 返回结果
            return Result.successDataList(dataList=data_list)

        elif request.crawler_way == "cron":
            # 获取爬虫信息
            crawlerInfo = db.query(CrawlerCron).filter(CrawlerCron.crawler_id == request.crawler_id).first()
            if not crawlerInfo:
                return Result.error(msg="未找到对应舆情预警任务！")

            if crawlerInfo.state != CrawlerCronTaskState.WAITTING and crawlerInfo.state != CrawlerCronTaskState.FAILED:
                return Result.error(msg=f"舆情预警任务状态错误：要求状态为{CRON_STATE_TEXT[CrawlerCronTaskState.WAITTING]}/{CRON_STATE_TEXT[CrawlerCronTaskState.FAILED]},当前状态为：{CRON_STATE_TEXT[crawlerInfo.state]}！")

            # 读取参数
            params_dict = crawlerInfo.params
            sources = list(params_dict.get("sources"))
            page = int(params_dict.get("page"))

            # 设置爬取状态
            crawler_old_state = crawlerInfo.state
            crawlerInfo.state = CrawlerCronTaskState.CRAWLING
            db.add(crawlerInfo)
            db.commit()

            # websocket给java发消息
            ws_msg = {
                "type": "crawler_cron_state_change",
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.crawler_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": CRON_STATE_TEXT[crawler_old_state],
                "crawler_new_state": CRON_STATE_TEXT[CrawlerCronTaskState.CRAWLING]
            }
            await java_ws.send(ws_msg)

            # 执行爬取
            keyword = crawlerInfo.key_word
            keywordGroups = keyword.get("keywordGroups")

            # 遍历分组 + 遍历每个关键词
            last_lists = []
            for group in keywordGroups:
                # 遍历爬取组内的每个词，将搜索结果合并
                cur_lists = []
                for word in group:
                    get_news_list = service.crawl_integration(
                        key_word=word,
                        sources=sources,
                        page=page
                    )
                    # 转换为字典列表
                    clear_news_list = [news.model_dump() for news in get_news_list]
                    cur_lists.append(clear_news_list)
                last_lists.append(merge_unique_news(cur_lists))

            news_list = list_intersect(last_lists)

            # 设置爬取状态
            crawler_old_state = CrawlerCronTaskState.CRAWLING
            crawlerInfo.state = CrawlerCronTaskState.CLEANING
            db.add(crawlerInfo)
            db.commit()

            # websocket给java发消息
            ws_msg = {
                "type": "crawler_none_state_change",
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.crawler_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": CRON_STATE_TEXT[crawler_old_state],
                "crawler_new_state": CRON_STATE_TEXT[CrawlerCronTaskState.CLEANING]
            }
            await java_ws.send(ws_msg)

            # 返回结果
            return Result.successDataList(dataList=news_list)
        else:
            return Result.error(f"无法识别的任务类型：{request.crawler_way}!")

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
