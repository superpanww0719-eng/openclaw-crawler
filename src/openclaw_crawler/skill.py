"""
OpenClaw Crawler Skill - 封装为 OpenClaw 可调用的 Skill
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

from .core.wechat_crawler import WechatCrawler
from .adapters.platform_adapter import PlatformAdapter
from .storage.database import DatabaseManager


@dataclass
class CrawlResult:
    """爬取结果"""
    success: bool
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class CrawlerSkill:
    """
    OpenClaw Crawler Skill
    
    封装爬虫能力为 OpenClaw 可调用的接口
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        初始化 Skill
        
        Args:
            db_url: 数据库连接 URL，如 postgresql://user:pass@localhost/crawler
        """
        self.wechat_crawler = WechatCrawler()
        self.platform_adapter = PlatformAdapter()
        self.db = DatabaseManager(db_url) if db_url else None
    
    def crawl(self, url: str, platform: str = "auto") -> CrawlResult:
        """
        爬取指定 URL
        
        Args:
            url: 目标 URL
            platform: 平台类型 (wechat/web/xiaohongshu/twitter 等)
        
        Returns:
            CrawlResult: 爬取结果
        """
        # 自动检测平台
        if platform == "auto":
            platform = self._detect_platform(url)
        
        try:
            if platform == "wechat":
                return self._crawl_wechat(url)
            elif platform in ["xiaohongshu", "twitter", "reddit", "bilibili"]:
                return self._crawl_platform(platform, url)
            else:
                return self._crawl_web(url)
        except Exception as e:
            return CrawlResult(
                success=False,
                url=url,
                error_message=str(e)
            )
    
    def crawl_batch(self, urls: List[str], platform: str = "auto") -> List[CrawlResult]:
        """
        批量爬取多个 URL
        
        Args:
            urls: URL 列表
            platform: 平台类型
        
        Returns:
            List[CrawlResult]: 爬取结果列表
        """
        results = []
        for url in urls:
            result = self.crawl(url, platform)
            results.append(result)
        return results
    
    def search_and_crawl(self, platform: str, query: str, limit: int = 10) -> List[CrawlResult]:
        """
        搜索并爬取
        
        Args:
            platform: 平台 (xiaohongshu/twitter/reddit/github 等)
            query: 搜索关键词
            limit: 结果数量限制
        
        Returns:
            List[CrawlResult]: 爬取结果列表
        """
        try:
            results = self.platform_adapter.search(platform, query, limit)
            return [CrawlResult(success=True, **r) for r in results]
        except Exception as e:
            return [CrawlResult(success=False, url="", error_message=str(e))]
    
    def _detect_platform(self, url: str) -> str:
        """自动检测平台类型"""
        if "mp.weixin.qq.com" in url:
            return "wechat"
        elif "xiaohongshu.com" in url or "xhslink.com" in url:
            return "xiaohongshu"
        elif "twitter.com" in url or "x.com" in url:
            return "twitter"
        elif "reddit.com" in url:
            return "reddit"
        elif "bilibili.com" in url:
            return "bilibili"
        else:
            return "web"
    
    def _crawl_wechat(self, url: str) -> CrawlResult:
        """爬取微信公众号文章"""
        result = self.wechat_crawler.crawl(url)
        return CrawlResult(success=True, **result)
    
    def _crawl_web(self, url: str) -> CrawlResult:
        """爬取普通网页"""
        from .core.web_crawler import WebCrawler
        crawler = WebCrawler()
        result = crawler.crawl(url)
        return CrawlResult(success=True, **result)
    
    def _crawl_platform(self, platform: str, url: str) -> CrawlResult:
        """通过 Agent-Reach 爬取特定平台"""
        result = self.platform_adapter.read_url(platform, url)
        return CrawlResult(success=True, **result)


# OpenClaw 调用接口
def crawl(url: str, platform: str = "auto") -> str:
    """
    OpenClaw 调用的主接口
    
    Args:
        url: 目标 URL
        platform: 平台类型
    
    Returns:
        str: JSON 格式的爬取结果
    """
    skill = CrawlerSkill()
    result = skill.crawl(url, platform)
    return result.to_json()


def crawl_batch(urls: List[str], platform: str = "auto") -> str:
    """
    批量爬取接口
    
    Args:
        urls: URL 列表
        platform: 平台类型
    
    Returns:
        str: JSON 格式的结果列表
    """
    skill = CrawlerSkill()
    results = skill.crawl_batch(urls, platform)
    return json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2)


def search(platform: str, query: str, limit: int = 10) -> str:
    """
    搜索接口
    
    Args:
        platform: 平台类型
        query: 搜索关键词
        limit: 结果数量
    
    Returns:
        str: JSON 格式的搜索结果
    """
    skill = CrawlerSkill()
    results = skill.search_and_crawl(platform, query, limit)
    return json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2)
