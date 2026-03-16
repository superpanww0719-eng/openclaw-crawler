FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml README.md ./
COPY src/ ./src/

# 安装 Python 依赖
RUN pip install --no-cache-dir -e ".[all]"

# 安装 Scrapling 浏览器依赖
RUN scrapling install --force || echo "Browser install skipped"

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "openclaw_crawler.cli"]
