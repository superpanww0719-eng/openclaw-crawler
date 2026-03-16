"""
OpenClaw Crawler - 企业级爬虫系统
"""

__version__ = "0.1.0"
__author__ = "OpenClaw Team"

from .skill import CrawlerSkill
from .core.crawler import BaseCrawler
from .adapters.platform_adapter import PlatformAdapter

__all__ = [
    "CrawlerSkill",
    "BaseCrawler", 
    "PlatformAdapter",
]
