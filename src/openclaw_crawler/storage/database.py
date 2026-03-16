"""
数据库存储管理
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
import json

try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
except ImportError:
    raise ImportError("请先安装 sqlalchemy: pip install sqlalchemy")


Base = declarative_base()


class CrawlTask(Base):
    """爬取任务表"""
    __tablename__ = 'crawl_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    target_url = Column(Text)
    status = Column(String(20), default='pending')  # pending/running/completed/failed
    priority = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_name": self.task_name,
            "platform": self.platform,
            "target_url": self.target_url,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }


class CrawlResult(Base):
    """爬取结果表"""
    __tablename__ = 'crawl_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer)
    url = Column(Text, nullable=False)
    title = Column(Text)
    content = Column(Text)
    author = Column(String(255))
    publish_time = Column(String(100))
    metadata = Column(JSON)
    raw_html = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "publish_time": self.publish_time,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DatabaseManager:
    """
    数据库管理器
    
    管理爬取任务和结果的存储
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        初始化
        
        Args:
            db_url: 数据库连接 URL
        """
        if db_url:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        else:
            self.engine = None
            self.Session = None
    
    def create_task(self, task_name: str, platform: str, target_url: str, priority: int = 5) -> int:
        """
        创建爬取任务
        
        Args:
            task_name: 任务名称
            platform: 平台类型
            target_url: 目标 URL
            priority: 优先级
        
        Returns:
            int: 任务 ID
        """
        if not self.Session:
            raise RuntimeError("数据库未配置")
        
        session = self.Session()
        try:
            task = CrawlTask(
                task_name=task_name,
                platform=platform,
                target_url=target_url,
                priority=priority,
                status='pending'
            )
            session.add(task)
            session.commit()
            return task.id
        finally:
            session.close()
    
    def update_task_status(self, task_id: int, status: str, error_message: Optional[str] = None):
        """更新任务状态"""
        if not self.Session:
            return
        
        session = self.Session()
        try:
            task = session.query(CrawlTask).filter_by(id=task_id).first()
            if task:
                task.status = status
                if error_message:
                    task.error_message = error_message
                
                if status == 'running':
                    task.started_at = datetime.utcnow()
                elif status in ['completed', 'failed']:
                    task.completed_at = datetime.utcnow()
                
                session.commit()
        finally:
            session.close()
    
    def save_result(self, task_id: int, url: str, title: Optional[str], 
                    content: Optional[str], author: Optional[str] = None,
                    publish_time: Optional[str] = None, metadata: Optional[Dict] = None):
        """保存爬取结果"""
        if not self.Session:
            return
        
        session = self.Session()
        try:
            result = CrawlResult(
                task_id=task_id,
                url=url,
                title=title,
                content=content,
                author=author,
                publish_time=publish_time,
                metadata=metadata or {}
            )
            session.add(result)
            session.commit()
        finally:
            session.close()
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        if not self.Session:
            return None
        
        session = self.Session()
        try:
            task = session.query(CrawlTask).filter_by(id=task_id).first()
            return task.to_dict() if task else None
        finally:
            session.close()
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取待处理任务"""
        if not self.Session:
            return []
        
        session = self.Session()
        try:
            tasks = session.query(CrawlTask).filter_by(status='pending').order_by(
                CrawlTask.priority.desc(),
                CrawlTask.created_at.asc()
            ).limit(limit).all()
            return [t.to_dict() for t in tasks]
        finally:
            session.close()
