# OpenClaw Crawler

基于 OpenClaw 的企业级爬虫系统，集成 Scrapling 和 Agent-Reach 能力。

## 特性

- 🕷️ **Scrapling 集成**: 内置反爬虫绕过、浏览器自动化
- 🔍 **Agent-Reach 支持**: 多平台数据抓取（小红书、Twitter、Reddit 等）
- 🗄️ **数据库存储**: PostgreSQL + Redis 架构
- 📊 **任务调度**: Celery 分布式任务队列
- 🐳 **容器化部署**: Docker + Docker Compose
- 🔧 **OpenClaw Skill**: 封装为可调用 Skill

## 快速开始

### 安装

```bash
pip install openclaw-crawler
```

### 作为 OpenClaw Skill 使用

```python
from openclaw_crawler import CrawlerSkill

skill = CrawlerSkill()
result = skill.crawl("https://mp.weixin.qq.com/s/xxxxx", platform="wechat")
```

### CLI 使用

```bash
# 爬取微信公众号文章
openclaw-crawler crawl "https://mp.weixin.qq.com/s/xxxxx" --platform wechat

# 爬取小红书
openclaw-crawler xiaohongshu "关键词" --limit 10
```

## 项目结构

```
openclaw-crawler/
├── src/
│   └── openclaw_crawler/
│       ├── __init__.py
│       ├── core/           # 核心爬虫引擎
│       ├── adapters/       # 平台适配器
│       ├── storage/        # 数据存储
│       ├── scheduler/      # 任务调度
│       └── skill.py        # OpenClaw Skill 封装
├── tests/
├── docker/
├── docs/
└── SKILL.md               # OpenClaw Skill 文档
```

## 许可证

MIT
