"""
报告生成服务 - 使用通义千问AI生成舆情报告
"""
import json
import logging
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime


class ReportGenerationService:
    """报告生成服务"""
    
    def __init__(self, ai_service):
        """
        初始化报告生成服务
        
        参数:
            ai_service: AI服务实例
        """
        self.ai_service = ai_service
    
    def clean_and_label_news(self, news_list: List[Dict]) -> List[Dict]:
        """
        批量清洗和标记新闻数据
        
        参数:
            news_list: 新闻数据列表
        
        返回:
            清洗标记结果列表
        """
        if not news_list:
            return []
        
        logging.info(f"开始清洗标记{len(news_list)}条新闻")
        
        # 构建批量清洗提示词
        prompt = self._build_clean_prompt(news_list)
        
        # 调用AI API
        ai_result = self.ai_service._call_qwen_api(prompt)
        
        if ai_result:
            # 解析AI返回的清洗结果
            clean_results = self._parse_clean_result(ai_result, news_list)
            return clean_results
        else:
            # AI调用失败，返回默认值
            logging.warning("AI清洗调用失败，使用默认值")
            return [self._default_clean_data(news) for news in news_list]
    
    def _build_clean_prompt(self, news_list: List[Dict]) -> str:
        """构建清洗标记提示词"""
        prompt = f"""你是舆情分析专家。我给你{len(news_list)}条新闻，请分析每条新闻的敏感度和情绪。

只返回JSON数组，不要其他文字！

返回格式示例：
[
  {{"sensitivity_level":0,"sensitivity_label":"无敏感","sentiment_type":1}},
  {{"sensitivity_level":2,"sensitivity_label":"政治敏感","sentiment_type":-1}}
]

字段说明：
- sensitivity_level: 敏感度等级（0不敏感/1低敏感/2中敏感/3高敏感）
- sensitivity_label: 敏感标签（无敏感/政治敏感/社会敏感/经济敏感/其他敏感）
- sentiment_type: 情绪极性（-1负面/0中性/1正面）

---

"""
        
        for idx, news in enumerate(news_list, 1):
            title = news.get("title", "")
            content = news.get("content", "")
            prompt += f"""新闻{idx}:
标题: {title}
内容: {content[:300]}...

"""
        
        prompt += f"\n请返回包含{len(news_list)}条新闻分析结果的JSON数组："
        return prompt
    
    def _parse_clean_result(self, ai_result: str, news_list: List[Dict]) -> List[Dict]:
        """解析AI清洗结果"""
        try:
            # 清理并提取JSON
            ai_result = ai_result.strip()
            start_idx = ai_result.find('[')
            end_idx = ai_result.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_result[start_idx:end_idx + 1]
                clean_data_list = json.loads(json_str)
                
                results = []
                for idx, clean_data in enumerate(clean_data_list):
                    if idx >= len(news_list):
                        break
                    
                    results.append({
                        "news_id": news_list[idx].get("news_id"),
                        "sensitivity_level": clean_data.get("sensitivity_level", 0),
                        "sensitivity_label": clean_data.get("sensitivity_label", "无敏感"),
                        "sentiment_type": clean_data.get("sentiment_type", 0)
                    })
                
                # 补充缺失的数据
                for idx in range(len(results), len(news_list)):
                    results.append(self._default_clean_data(news_list[idx]))
                
                return results
            else:
                raise ValueError("未找到JSON数组")
                
        except Exception as e:
            logging.error(f"解析清洗结果失败: {e}")
            return [self._default_clean_data(news) for news in news_list]
    
    def _default_clean_data(self, news: Dict) -> Dict:
        """默认清洗数据"""
        return {
            "news_id": news.get("news_id"),
            "sensitivity_level": 0,
            "sensitivity_label": "无敏感",
            "sentiment_type": 0
        }
    
    def generate_report(self, news_list: List[Dict], clean_data_list: List[Dict], 
                       special_report_id: int, report_type: str, keywords: List[str]) -> Dict:
        """
        生成舆情报告
        
        参数:
            news_list: 新闻数据列表
            clean_data_list: 清洗标记数据列表
            special_report_id: 专题报告ID
            keywords: 监测关键词
        
        返回:
            报告数据字典
        """
        logging.info(f"开始生成舆情报告，新闻数量: {len(news_list)}")
        
        # 统计分析
        stats = self._calculate_statistics(news_list, clean_data_list)
        
        # 使用AI生成报告各部分
        report_data = {
            "special_report_id": special_report_id,
            "report_name": f"舆情报告_{datetime.now().strftime('%Y%m%d')}",
            "monitor_keywords": keywords,
            "report_type": report_type,
            "brief_summary": self._generate_brief_summary(stats),
            "monitor_summary": self._generate_monitor_summary(stats),
            "opinion_trend": self._generate_opinion_trend(news_list, stats),
            "source_media_analysis": self._generate_source_media_analysis(stats),
            "emotion_analysis": self._generate_emotion_analysis(stats),
            "region_distribution": self._generate_region_distribution(stats),
            "hot_analysis_words": self._generate_hot_words(news_list),
            "hot_information": self._generate_hot_information(news_list, clean_data_list),
            "disposal_opinions": self._generate_disposal_opinions(stats)
        }
        
        return report_data

    def _calculate_statistics(self, news_list: List[Dict], clean_data_list: List[Dict]) -> Dict:
        """计算统计数据"""
        total = len(news_list)

        # 平台统计
        platform_counter = Counter([news.get("platform", "未知") for news in news_list])

        # 情绪统计
        sentiment_counter = Counter([clean.get("sentiment_type", 0) for clean in clean_data_list])

        # 敏感度统计
        sensitivity_counter = Counter([clean.get("sensitivity_level", 0) for clean in clean_data_list])

        # 地区统计
        region_counter = Counter([news.get("region", "未知") for news in news_list if news.get("region")])

        # 时间分布
        time_distribution = self._analyze_time_distribution(news_list)

        return {
            "total": total,
            "platform_stats": dict(platform_counter.most_common(5)),
            "sentiment_stats": {
                "positive": sentiment_counter.get(1, 0),
                "neutral": sentiment_counter.get(0, 0),
                "negative": sentiment_counter.get(-1, 0)
            },
            "sensitivity_stats": {
                "level_0": sensitivity_counter.get(0, 0),
                "level_1": sensitivity_counter.get(1, 0),
                "level_2": sensitivity_counter.get(2, 0),
                "level_3": sensitivity_counter.get(3, 0)
            },
            "region_stats": dict(region_counter.most_common(10)),
            "time_distribution": time_distribution
        }

    def _analyze_time_distribution(self, news_list: List[Dict]) -> Dict:
        """分析时间分布"""
        time_counter = Counter()
        for news in news_list:
            publish_time = news.get("publish_time")
            if publish_time:
                if isinstance(publish_time, str):
                    date_str = publish_time.split()[0]
                else:
                    date_str = publish_time.strftime("%Y-%m-%d")
                time_counter[date_str] += 1

        return dict(time_counter)

    def _generate_brief_summary(self, stats: Dict) -> str:
        """生成简版概述"""
        total = stats["total"]
        platform_stats = stats["platform_stats"]

        # 构建平台占比描述
        platform_desc = []
        for platform, count in list(platform_stats.items())[:5]:
            percentage = (count / total * 100) if total > 0 else 0
            platform_desc.append(f"{platform}{count}篇，占比{percentage:.1f}%")

        summary = f"本报告对监测的{total}篇文章进行分析，"
        summary += f"文章占比前五的平台包含：{';'.join(platform_desc)}。"
        summary += "详细报告请继续浏览。"

        return summary

    def _generate_monitor_summary(self, stats: Dict) -> str:
        """生成监测概述"""
        total = stats["total"]
        sentiment = stats["sentiment_stats"]

        positive = sentiment["positive"]
        neutral = sentiment["neutral"]
        negative = sentiment["negative"]

        summary = f"监测主题相关信息{total}条，其中"
        summary += f"正面信息{positive}条，占比{(positive/total*100):.1f}%；"
        summary += f"中性信息{neutral}条，占比{(neutral/total*100):.1f}%；"
        summary += f"负面信息{negative}条，占比{(negative/total*100):.1f}%。"

        return summary

    def _generate_opinion_trend(self, news_list: List[Dict], stats: Dict) -> str:
        """生成舆情发展趋势"""
        time_dist = stats["time_distribution"]
        total = stats["total"]

        if not time_dist:
            return "暂无时间分布数据"

        dates = sorted(time_dist.keys())
        start_date = dates[0] if dates else "未知"
        end_date = dates[-1] if dates else "未知"

        avg_daily = total / len(dates) if dates else 0

        trend = f"在{start_date}至{end_date}监测期间，"
        trend += f"舆情信息量共计{total}条，日平均舆情信息量为{avg_daily:.0f}条。"

        # 找出峰值日期
        if time_dist:
            peak_date = max(time_dist, key=time_dist.get)
            peak_count = time_dist[peak_date]
            trend += f"其中{peak_date}达到峰值{peak_count}条。"

        return trend

    def _generate_source_media_analysis(self, stats: Dict) -> str:
        """生成来源媒体分析"""
        platform_stats = stats["platform_stats"]
        total = stats["total"]

        analysis = "来源媒体分布如下：\n"
        for platform, count in platform_stats.items():
            percentage = (count / total * 100) if total > 0 else 0
            analysis += f"{platform}：{count}条，占比{percentage:.1f}%\n"

        return analysis

    def _generate_emotion_analysis(self, stats: Dict) -> str:
        """生成情绪分析"""
        sentiment = stats["sentiment_stats"]
        total = stats["total"]

        positive = sentiment["positive"]
        neutral = sentiment["neutral"]
        negative = sentiment["negative"]

        analysis = "情绪分析结果：\n"
        analysis += f"正面舆情：{positive}条，占比{(positive/total*100):.1f}%\n"
        analysis += f"中性舆情：{neutral}条，占比{(neutral/total*100):.1f}%\n"
        analysis += f"负面舆情：{negative}条，占比{(negative/total*100):.1f}%\n"

        if negative > positive:
            analysis += "\n负面舆情占比较高，需要重点关注。"
        elif positive > negative * 2:
            analysis += "\n正面舆情占主导，整体舆论环境良好。"
        else:
            analysis += "\n舆情情绪较为平衡。"

        return analysis

    def _generate_region_distribution(self, stats: Dict) -> str:
        """生成地域分布"""
        region_stats = stats["region_stats"]
        total = sum(region_stats.values()) if region_stats else 0

        if not region_stats:
            return "暂无地域分布数据"

        distribution = "地域分布排名：\n"
        for idx, (region, count) in enumerate(region_stats.items(), 1):
            percentage = (count / total * 100) if total > 0 else 0
            distribution += f"{idx}. {region}：{count}条，占比{percentage:.2f}%\n"

        return distribution

    def _generate_hot_words(self, news_list: List[Dict]) -> str:
        """生成热分析词"""
        # 提取所有标题和内容中的词
        all_text = []
        for news in news_list:
            title = news.get("title", "")
            content = news.get("content", "")
            all_text.append(title + " " + content)

        # 简单的词频统计（实际应该使用jieba分词）
        word_counter = Counter()
        for text in all_text:
            # 简单按空格和标点分词
            words = text.replace("，", " ").replace("。", " ").replace("、", " ").split()
            for word in words:
                if len(word) >= 2:  # 只统计2个字以上的词
                    word_counter[word] += 1

        # 生成热词分析
        hot_words = "热词分析（前20）：\n"
        for idx, (word, count) in enumerate(word_counter.most_common(20), 1):
            percentage = (count / len(news_list) * 100) if news_list else 0
            hot_words += f"{idx}. {word}：出现{count}次，占比{percentage:.1f}%\n"

        return hot_words

    def _generate_hot_information(self, news_list: List[Dict], clean_data_list: List[Dict]) -> str:
        """生成热门信息"""
        # 按评论数排序（如果有的话）
        news_with_clean = []
        for news in news_list:
            clean = next((c for c in clean_data_list if c.get("news_id") == news.get("news_id")), {})
            news_with_clean.append({**news, **clean})

        # 按评论数排序，取前10条
        sorted_news = sorted(
            news_with_clean,
            key=lambda x: x.get("comment", 0) or 0,
            reverse=True
        )[:10]

        hot_info = "热门信息TOP10：\n\n"
        for idx, news in enumerate(sorted_news, 1):
            title = news.get("title", "未知标题")
            platform = news.get("platform", "未知平台")
            publisher = news.get("publisher", "未知")
            sentiment = news.get("sentiment_type", 0)
            sentiment_text = {1: "正面", 0: "中性", -1: "负面"}.get(sentiment, "未知")
            publish_time = news.get("publish_time", "未知时间")
            comment_count = news.get("comment", 0) or 0

            hot_info += f"{idx}. {title}\n"
            hot_info += f"   平台：{platform} | 发布者：{publisher} | 情绪：{sentiment_text}\n"
            hot_info += f"   时间：{publish_time} | 评论数：{comment_count}\n\n"

        return hot_info

    def _generate_disposal_opinions(self, stats: Dict) -> str:
        """生成处置意见"""
        sentiment = stats["sentiment_stats"]
        sensitivity = stats["sensitivity_stats"]

        negative = sentiment["negative"]
        high_sensitivity = sensitivity["level_3"]
        medium_sensitivity = sensitivity["level_2"]

        opinions = "处置意见：\n\n"

        if high_sensitivity > 0:
            opinions += f"1. 高敏感信息处置：检测到{high_sensitivity}条高敏感信息，建议立即核实并采取应对措施。\n\n"

        if medium_sensitivity > 0:
            opinions += f"2. 中敏感信息监控：检测到{medium_sensitivity}条中敏感信息，建议持续关注舆情走向。\n\n"

        if negative > sentiment["positive"]:
            opinions += f"3. 负面舆情应对：负面信息占比较高（{negative}条），建议：\n"
            opinions += "   - 及时发布官方声明澄清事实\n"
            opinions += "   - 加强正面信息引导\n"
            opinions += "   - 与重点媒体保持沟通\n\n"

        opinions += "4. 日常监测建议：\n"
        opinions += "   - 保持7×24小时舆情监测\n"
        opinions += "   - 建立快速响应机制\n"
        opinions += "   - 定期生成舆情分析报告\n"

        return opinions

