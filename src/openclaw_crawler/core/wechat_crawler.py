"""
微信公众号文章爬虫 - 专门处理微信的反爬虫机制
"""

import asyncio
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

try:
    from scrapling.fetchers import StealthyFetcher, StealthySession
    from scrapling.parser import Selector
except ImportError:
    raise ImportError("请先安装 scrapling: pip install 'scrapling[all]>=0.4.2'")


class WechatCrawler:
    """
    微信公众号文章爬虫
    
    特性：
    - 自动绕过微信的反爬虫检测
    - 支持滑块验证码检测
    - 提取文章完整内容
    """
    
    def __init__(self):
        self.session = None
    
    def _init_session(self):
        """初始化 Stealthy 会话"""
        if self.session is None:
            self.session = StealthySession(
                headless=True,
                solve_cloudflare=True,
                block_webrtc=True,
                hide_canvas=True,
            )
    
    def crawl(self, url: str) -> Dict[str, Any]:
        """
        爬取微信公众号文章
        
        Args:
            url: 微信公众号文章链接
        
        Returns:
            Dict: 包含 title, author, content, publish_time 等字段
        """
        return self._crawl_sync(url)
    
    def _crawl_sync(self, url: str) -> Dict[str, Any]:
        """同步爬取实现"""
        self._init_session()
        
        try:
            # 使用 stealthy-fetch 绕过反爬虫
            page = self.session.fetch(
                url,
                network_idle=True,
                wait=3000,  # 等待页面加载完成
            )
            
            # 检查是否遇到验证码页面
            if self._is_captcha_page(page):
                return {
                    "url": url,
                    "title": None,
                    "content": None,
                    "author": None,
                    "publish_time": None,
                    "metadata": {
                        "requires_captcha": True,
                        "message": "遇到微信安全验证，请在微信客户端中打开此链接"
                    }
                }
            
            # 提取文章信息
            result = self._extract_article(page, url)
            return result
            
        except Exception as e:
            return {
                "url": url,
                "title": None,
                "content": None,
                "author": None,
                "publish_time": None,
                "metadata": {"error": str(e)}
            }
    
    def _is_captcha_page(self, page) -> bool:
        """检查是否遇到验证码页面"""
        # 检查页面内容特征
        title = page.css('title::text').get('')
        body_text = page.css('body::text').get('')
        
        captcha_indicators = [
            '环境异常',
            '安全验证',
            '拖动下方滑块',
            '完成验证后即可继续访问',
        ]
        
        for indicator in captcha_indicators:
            if indicator in title or indicator in body_text:
                return True
        
        # 检查是否有验证码 iframe
        if page.css('iframe[src*="wappoc_appmsgcaptcha"]'):
            return True
        
        return False
    
    def _extract_article(self, page, url: str) -> Dict[str, Any]:
        """提取文章内容"""
        # 标题 - 尝试多种选择器
        title = (
            page.css('#activity_name::text').get('') or
            page.css('h1.rich_media_title::text').get('') or
            page.css('h1::text').get('') or
            page.css('meta[property="og:title"]::attr(content)').get('')
        ).strip()
        
        # 作者
        author = (
            page.css('#js_name::text').get('') or
            page.css('.profile_nickname::text').get('') or
            page.css('.rich_media_meta_nickname::text').get('') or
            page.css('meta[property="og:article:author"]::attr(content)').get('')
        ).strip()
        
        # 发布时间
        publish_time = (
            page.css('#publish_time::text').get('') or
            page.css('.rich_media_meta_text::text').get('') or
            page.css('em#publish_time::text').get('')
        ).strip()
        
        # 文章内容
        content_html = page.css('#js_content').get('')
        content_text = page.css('#js_content::text').get('')
        
        # 提取所有段落文本
        paragraphs = page.css('#js_content p::text').getall()
        full_text = '\n'.join([p.strip() for p in paragraphs if p.strip()])
        
        # 提取图片
        images = page.css('#js_content img::attr(data-src)').getall()
        if not images:
            images = page.css('#js_content img::attr(src)').getall()
        
        # 阅读量、点赞数等元数据
        read_count = self._extract_number(page, '.read-count, #readNum')
        like_count = self._extract_number(page, '.like-count, #likeNum')
        
        return {
            "url": url,
            "title": title,
            "content": full_text or content_text,
            "content_html": content_html,
            "author": author,
            "publish_time": publish_time,
            "metadata": {
                "images": images,
                "read_count": read_count,
                "like_count": like_count,
                "requires_captcha": False,
            }
        }
    
    def _extract_number(self, page, selector: str) -> Optional[int]:
        """提取数字"""
        text = page.css(selector + '::text').get('')
        if text:
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
        return None
    
    def __del__(self):
        """清理资源"""
        if self.session:
            try:
                self.session.close()
            except:
                pass
