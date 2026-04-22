"""
AI服务 - 使用通义千问API补全新闻数据
"""
import requests
import json
from typing import Dict, Optional
from datetime import datetime
import logging


class AIService:
    """AI服务，使用通义千问API分析URL并补全新闻数据"""

    def __init__(self, api_key: str):
        """
        初始化AI服务

        参数:
            api_key: 通义千问API密钥
        """
        self.api_key = api_key
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model = "qwen-plus"

    def enrich_news_data(self, url: str, basic_data: Dict) -> Dict:
        """
        访问URL并使用通义千问AI补全新闻数据

        参数:
            url: 新闻URL
            basic_data: 基础数据（从爬虫获取的数据）

        返回:
            补全后的新闻数据字典
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(url, basic_data)

            # 调用通义千问API
            ai_result = self._call_qwen_api(prompt)

            if ai_result:
                # 解析AI返回的JSON
                enriched_data = self._parse_ai_result(ai_result, basic_data, url)
                return enriched_data
            else:
                # AI调用失败，返回基础数据
                return self._build_fallback_data(basic_data, url)

        except Exception as e:
            logging.error(f"AI补全数据失败: {e}")
            return self._build_fallback_data(basic_data, url)

    def _build_prompt(self, url: str, basic_data: Dict) -> str:
        """构建发送给AI的提示词"""
        title = basic_data.get("title", "")
        content = basic_data.get("content", "")
        source = basic_data.get("source", "")
        publish_time = basic_data.get("publishTime", "")

        prompt = f"""你是舆情分析专家，严格按JSON输出，不要多余文字：
{{
    "title": "文章标题",
    "content": "150字内摘要",
    "publisher": "发布者/作者",
    "publish_time": "YYYY-MM-DD HH:MM:SS",
    "video": true/false,
    "source": "来源平台",
    "comment_count": 数字,
    "region": "地区",
    "article_type": "新闻/资讯/评论/视频/推广"
}}

请分析以下新闻信息：
URL: {url}
标题: {title}
内容: {content}
来源: {source}
发布时间: {publish_time}

请根据以上信息，补全并返回JSON格式的数据。"""

        return prompt

    def _call_qwen_api(self, prompt: str) -> Optional[str]:
        """
        调用通义千问API

        参数:
            prompt: 提示词

        返回:
            AI返回的文本内容
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # 降低随机性，提高准确性
                "max_tokens": 1000
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content
            else:
                logging.error(f"通义千问API调用失败: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logging.error(f"调用通义千问API异常: {e}")
            return None

    def _parse_ai_result(self, ai_result: str, basic_data: Dict, url: str) -> Dict:
        """
        解析AI返回的JSON结果

        参数:
            ai_result: AI返回的文本
            basic_data: 基础数据
            url: 原始URL

        返回:
            解析后的数据字典
        """
        try:
            # 尝试提取JSON部分
            ai_result = ai_result.strip()

            # 如果有代码块标记，去除它们
            if ai_result.startswith("```json"):
                ai_result = ai_result[7:]
            if ai_result.startswith("```"):
                ai_result = ai_result[3:]
            if ai_result.endswith("```"):
                ai_result = ai_result[:-3]

            ai_result = ai_result.strip()

            # 解析JSON
            ai_data = json.loads(ai_result)

            # 构建最终数据
            enriched_data = {
                "title": ai_data.get("title", basic_data.get("title", "")),
                "content": ai_data.get("content", basic_data.get("content", "")),
                "video": ai_data.get("video"),
                "platform": self._extract_platform(url),
                "source": ai_data.get("source", basic_data.get("source", "")),
                "publisher": ai_data.get("publisher"),
                "publish_time": self._parse_publish_time(ai_data.get("publish_time")),
                "comment": ai_data.get("comment_count"),
                "region": ai_data.get("region"),
                "original_url": url,
                "article_type": ai_data.get("article_type"),
                "source_url": url,
            }

            return enriched_data

        except json.JSONDecodeError as e:
            logging.error(f"解析AI返回的JSON失败: {e}, 原始内容: {ai_result}")
            return self._build_fallback_data(basic_data, url)
        except Exception as e:
            logging.error(f"处理AI结果异常: {e}")
            return self._build_fallback_data(basic_data, url)

    def _build_fallback_data(self, basic_data: Dict, url: str) -> Dict:
        """
        构建降级数据（当AI调用失败时使用）

        参数:
            basic_data: 基础数据
            url: 原始URL

        返回:
            降级数据字典
        """
        return {
            "title": basic_data.get("title", ""),
            "content": basic_data.get("content", ""),
            "video": None,
            "platform": self._extract_platform(url),
            "source": basic_data.get("source", ""),
            "publisher": None,
            "publish_time": self._parse_publish_time(basic_data.get("publishTime")),
            "comment": None,
            "region": None,
            "original_url": url,
            "article_type": None,
            "source_url": url,
        }

    def _extract_platform(self, url: str) -> Optional[str]:
        """从URL提取平台名称"""
        if not url:
            return None
        
        # 简单的平台识别逻辑
        if "weibo.com" in url:
            return "微博"
        elif "toutiao.com" in url:
            return "今日头条"
        elif "163.com" in url:
            return "网易"
        elif "sina.com" in url:
            return "新浪"
        elif "qq.com" in url:
            return "腾讯"
        elif "news.china.com" in url:
            return "中华网"
        elif "www.ithome.com" in url:
            return "IT之家"
        elif "kepu.gmw.cn" in url:
            return "光明网"
        else:
            # 提取域名作为平台
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                return domain
            except:
                return None
    
    def _parse_publish_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析发布时间字符串为datetime对象"""
        if not time_str:
            return None
        
        try:
            # 尝试多种时间格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d",
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败，返回None
            return None
            
        except Exception as e:
            print(f"解析时间失败: {e}")
            return None
