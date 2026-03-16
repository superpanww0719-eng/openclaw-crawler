---
name: openclaw-crawler
description: |
  OpenClaw 企业级爬虫系统，集成 Scrapling 和 Agent-Reach 能力。
  支持微信公众号、小红书、Twitter、Reddit 等多平台数据抓取。
  内置反爬虫绕过、浏览器自动化、任务调度等功能。
triggers:
  - 爬虫
  - 爬取
  - 抓取
  - wechat
  - 微信公众号
  - xiaohongshu
  - 小红书
  - scraper
  - crawler
version: 0.1.0
author: OpenClaw Team
---

# OpenClaw Crawler Skill

企业级爬虫系统，基于 Scrapling 和 Agent-Reach 构建。

## 功能特性

- 🕷️ **多平台支持**: 微信公众号、小红书、Twitter、Reddit、B站等
- 🛡️ **反爬虫绕过**: 自动处理 Cloudflare、微信安全验证等
- 🤖 **浏览器自动化**: 支持 JS 渲染页面爬取
- 📊 **任务调度**: Celery 分布式任务队列
- 🗄️ **数据存储**: PostgreSQL + Redis 架构
- 🔧 **OpenClaw 集成**: 封装为可调用的 Skill

## 安装

```bash
pip install openclaw-crawler
```

## 使用方法

### 1. 爬取微信公众号文章

```python
from openclaw_crawler import CrawlerSkill

skill = CrawlerSkill()
result = skill.crawl("https://mp.weixin.qq.com/s/xxxxx", platform="wechat")

print(result.title)
print(result.author)
print(result.content)
```

### 2. 搜索小红书

```python
results = skill.search_and_crawl("xiaohongshu", "Python教程", limit=10)
for r in results:
    print(r.title, r.url)
```

### 3. CLI 使用

```bash
# 爬取微信公众号
openclaw-crawler crawl "https://mp.weixin.qq.com/s/xxxxx" --platform wechat

# 搜索小红书
openclaw-crawler search xiaohongshu "Python教程" --limit 5

# 测试爬取
openclaw-crawler test "https://mp.weixin.qq.com/s/xxxxx"
```

## API 参考

### CrawlerSkill

主 Skill 类，提供统一的爬取接口。

#### crawl(url, platform="auto")

爬取指定 URL。

**参数:**
- `url`: 目标 URL
- `platform`: 平台类型 (wechat/web/xiaohongshu/twitter/reddit/bilibili/github)

**返回:** `CrawlResult`

#### search_and_crawl(platform, query, limit=10)

搜索并爬取。

**参数:**
- `platform`: 平台名称
- `query`: 搜索关键词
- `limit`: 结果数量

**返回:** `List[CrawlResult]`

### CrawlResult

爬取结果数据类。

**属性:**
- `success`: 是否成功
- `url`: 目标 URL
- `title`: 标题
- `content`: 内容
- `author`: 作者
- `publish_time`: 发布时间
- `metadata`: 元数据字典

## 配置

### 数据库配置

```python
skill = CrawlerSkill(db_url="postgresql://user:pass@localhost/crawler")
```

### 环境变量

```bash
export CRAWLER_DB_URL="postgresql://user:pass@localhost/crawler"
export CRAWLER_REDIS_URL="redis://localhost:6379/0"
```

## 注意事项

1. **遵守 robots.txt**: 爬取前检查目标网站的 robots.txt
2. **控制频率**: 设置合理的爬取间隔，避免对目标网站造成压力
3. **法律合规**: 不爬取个人隐私数据，遵守相关法律法规
4. **微信验证**: 微信公众号文章可能需要微信客户端验证

## 依赖

- Python 3.10+
- Scrapling >= 0.4.2
- Celery >= 5.3.0
- SQLAlchemy >= 2.0.0
- PostgreSQL (可选)
- Redis (可选)

## 许可证

MIT
