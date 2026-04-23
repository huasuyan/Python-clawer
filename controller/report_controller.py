"""
报告生成控制器
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from common.result import Result
from config.db import get_db
from config.settings import settings
from entity.crawler_model import NewsData, ClearData, ReportResult, SpecialReportSetting
from service.ai_service import AIService
from service.report_generation_service import ReportGenerationService

router = APIRouter(prefix="/api/python/report", tags=["报告生成接口"])

# 服务实例
ai_service = None
report_service = None


def get_ai_service():
    """获取AI服务实例"""
    global ai_service
    if ai_service is None:
        if not settings.QWEN_API_KEY:
            logging.error("请配置通义千问API密钥！")
            raise HTTPException(status_code=500, detail="通义千问API密钥未配置")
        ai_service = AIService(api_key=settings.QWEN_API_KEY)
    return ai_service


def get_report_service():
    """获取报告生成服务实例"""
    global report_service
    if report_service is None:
        ai = get_ai_service()
        report_service = ReportGenerationService(ai_service=ai)
    return report_service


@router.get("/generateReport")
async def generate_report(special_report_id: int, db: Session = Depends(get_db)):
    """
    生成舆情报告
    
    参数:
        special_report_id: 专题报告ID
    
    流程:
        1. 查询news_data表获取新闻数据
        2. 使用AI清洗标记数据并存入clear_data表
        3. 使用AI生成舆情报告并存入report_result表
        4. 返回报告结果
    
    返回:
        {
            "code": 1,
            "msg": "success",
            "data": {
                "report_id": 1,
                "report_name": "舆情报告_20250108",
                "brief_summary": "...",
                ...
            }
        }
    """
    try:
        logging.info(f"开始生成舆情报告，special_report_id: {special_report_id}")
        
        # 1. 查询专题报告设置
        report_setting = db.query(SpecialReportSetting).filter(
            and_(
                SpecialReportSetting.special_report_id == special_report_id,
            )
        ).first()
        
        if not report_setting:
            return Result.error(msg="未找到对应的专题报告设置！")
        
        # 2. 查询news_data表获取新闻数据
        news_data_list = db.query(NewsData).filter(
            and_(
                NewsData.special_report_id == special_report_id,
                NewsData.is_report_need == 1
            )
        ).all()
        
        if not news_data_list:
            return Result.error(msg="未找到相关新闻数据，请先执行数据采集！")
        
        logging.info(f"查询到{len(news_data_list)}条新闻数据")
        
        # 转换为字典列表
        news_list = []
        for news in news_data_list:
            news_dict = {
                "news_id": news.news_id,
                "title": news.title,
                "content": news.content,
                "platform": news.platform,
                "source": news.source,
                "publisher": news.publisher,
                "publish_time": news.publish_time,
                "comment": news.comment,
                "region": news.region,
                "original_url": news.original_url,
                "article_type": news.article_type
            }
            news_list.append(news_dict)
        
        # 3. 使用AI清洗标记数据
        report_gen_service = get_report_service()
        
        logging.info("开始AI清洗标记...")
        clean_data_list = report_gen_service.clean_and_label_news(news_list)
        
        # 4. 保存清洗数据到clear_data表
        logging.info("保存清洗数据到数据库...")
        for clean_data in clean_data_list:
            # 检查是否已存在
            existing = db.query(ClearData).filter(
                ClearData.news_id == clean_data["news_id"]
            ).first()
            
            if existing:
                # 更新
                existing.sensitivity_level = clean_data["sensitivity_level"]
                existing.sensitivity_label = clean_data["sensitivity_label"]
                existing.sentiment_type = clean_data["sentiment_type"]
            else:
                # 新增
                clear_record = ClearData(
                    news_id=clean_data["news_id"],
                    sensitivity_level=clean_data["sensitivity_level"],
                    sensitivity_label=clean_data["sensitivity_label"],
                    sentiment_type=clean_data["sentiment_type"]
                )
                db.add(clear_record)
        
        db.commit()
        logging.info("清洗数据保存完成")
        
        # 5. 生成舆情报告
        logging.info("开始生成舆情报告...")
        monitor_keywords = report_setting.monitor_keywords
        
        report_data = report_gen_service.generate_report(
            news_list=news_list,
            clean_data_list=clean_data_list,
            special_report_id=special_report_id,
            keywords=monitor_keywords
        )
        
        # 6. 保存报告到report_result表
        logging.info("保存报告到数据库...")


        if settings.SAVE_MODE == "add":
            report_record = ReportResult(**report_data)
            db.add(report_record)
            db.flush()
            report_id = report_record.report_id
        else:
            # 检查是否已存在报告
            existing_report = db.query(ReportResult).filter(
                ReportResult.special_report_id == special_report_id
            ).first()

            if existing_report:
                # 更新现有报告
                for key, value in report_data.items():
                    if key != "special_report_id":
                        setattr(existing_report, key, value)
                report_id = existing_report.report_id
            else:
                # 创建新报告
                report_record = ReportResult(**report_data)
                db.add(report_record)
                db.flush()
                report_id = report_record.report_id

            db.commit()
            logging.info(f"报告生成完成，report_id: {report_id}")


        # 7. 将新闻标记为不需要生成报告
        db.query(NewsData) \
            .filter(
            and_(
                NewsData.special_report_id == special_report_id,
                NewsData.is_report_need == 1
            )
        ).update(
            {"is_report_need": 0}
        )

        db.commit()


        # 8. 返回报告结果
        result_report = db.query(ReportResult).filter(
            ReportResult.report_id == report_id
        ).first()
        
        report_dict = {
            "report_id": result_report.report_id,
            "special_report_id": result_report.special_report_id,
            "report_name": result_report.report_name,
            "monitor_keywords": result_report.monitor_keywords,
            "report_type": result_report.report_type,
            "brief_summary": result_report.brief_summary,
            "monitor_summary": result_report.monitor_summary,
            "opinion_trend": result_report.opinion_trend,
            "source_media_analysis": result_report.source_media_analysis,
            "emotion_analysis": result_report.emotion_analysis,
            "region_distribution": result_report.region_distribution,
            "hot_analysis_words": result_report.hot_analysis_words,
            "hot_information": result_report.hot_information,
            "disposal_opinions": result_report.disposal_opinions,
            "create_time": result_report.create_time.strftime("%Y-%m-%d %H:%M:%S") if result_report.create_time else None,
            "update_time": result_report.update_time.strftime("%Y-%m-%d %H:%M:%S") if result_report.update_time else None
        }
        
        return Result.success(data=report_dict, msg="报告生成成功")
        
    except Exception as e:
        logging.error(f"生成报告失败: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")
