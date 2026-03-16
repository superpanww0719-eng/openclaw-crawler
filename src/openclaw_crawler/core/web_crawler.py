"""
通用网页爬虫
"""

import asyncio
from typing import Dict, Any, Optional

try:
    from scrapling.fetchers import Fetcher, AsyncFetcher
    from scrapling.parser import Selector
except ImportError:
    raise ImportError("请先安装 scrapling: pip install 'scrapling[all]>=0.4.2'")


class WebCrawler:
    """
    通用网页爬虫
    
    支持普通 HTTP 请求和浏览器渲染两种模式
    """
    
    def __init__(self, use_browser: bool = False):
        """
        初始化
        
        Args:
            use_browser: 是否使用浏览器模式（用于 JS 渲染的页面）
        """
        self.use_browser = use_browser
    
    def crawl(self, url: str) -> Dict[str, Any]:
        """
        爬取网页
        
        Args:
            url: 目标 URL
        
        Returns:
            Dict: 包含 title, content, metadata 等
        """
        if self.use_browser:
            return asyncio.run(self._crawl_with_browser(url))
        else:
            return self._crawl_simple(url)
    
    def _crawl_simple(self, url: str) -> Dict[str, Any]:
        """简单 HTTP 请求爬取"""
        try:
            page = Fetcher.get(url, stealthy_headers=True)
            
            return {
                "url": url,
                "title": page.css('title::text').get(''),
                "content": page.css('body::text').get(''),
                "content_html": page.css('body').get(''),
                "metadata": {
                    "description": page.css('meta[name="description"]::attr(content)').get(''),
                    "keywords": page.css('meta[name="keywords"]::attr(content)').get(''),
                    "og_title": page.css('meta[property="og:title"]::attr(content)').get(''),
                    "og_image": page.css('meta[property="og:image"]::attr(content)').get(''),
                }
            }
        except Exception as e:
            return {
                "url": url,
                "title": None,
                "content": None,
                "metadata": {"error": str(e)}
            }
    
    async def _crawl_with_browser(self, url: str) -> Dict[str, Any]:
        """使用浏览器渲染爬取"""
        try:
            page = await AsyncFetcher.fetch(
                url,
                network_idle=True,
                wait=2000,
            )
            
            return {
                "url": url,
                "title": page.css('title::text').get(''),
                "content": page.css('body::text').get(''),
                "content_html": page.css('body').get(''),
                "metadata": {
                    "rendered": True,
                    "description": page.css('meta[name="description"]::attr(content)').get(''),
                }
            }
        except Exception as e:
            return {
                "url": url,
                "title": None,
                "content": None,
                "metadata": {"error": str(e), "rendered": True}
            }


class BaseCrawler:
    """
    爬虫基类 - 用于扩展自定义爬虫
    """
    
    def __init__(self):
        self.results = []
    
    def crawl(self, url: str) -> Dict[str, Any]:
        """
        爬取方法 - 子类需要重写
        
        Args:
            url: 目标 URL
        
        Returns:
            Dict: 爬取结果
        """
        raise NotImplementedError("子类必须实现 crawl 方法")
    
    def crawl_batch(self, urls: list) -> list:
        """
        批量爬取
        
        Args:
            urls: URL 列表
        
        Returns:
            list: 结果列表
        """
        results = []
        for url in urls:
            result = self.crawl(url)
            results.append(result)
        return results
