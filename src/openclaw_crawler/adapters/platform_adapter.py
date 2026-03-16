"""
平台适配器 - 集成 Agent-Reach 能力
"""

import subprocess
import json
import re
from typing import List, Dict, Any, Optional


class PlatformAdapter:
    """
    多平台适配器
    
    通过 Agent-Reach 调用各平台爬虫
    """
    
    PLATFORM_COMMANDS = {
        'xiaohongshu': 'agent-reach search-xhs',
        'twitter': 'agent-reach search-twitter',
        'reddit': 'agent-reach search-reddit',
        'github': 'agent-reach search-github',
        'youtube': 'agent-reach search-youtube',
        'bilibili': 'agent-reach search-bilibili',
        'instagram': 'agent-reach search-instagram',
        'linkedin': 'agent-reach search-linkedin',
    }
    
    def __init__(self):
        self.available_platforms = self._check_platforms()
    
    def _check_platforms(self) -> Dict[str, bool]:
        """检查各平台是否可用"""
        available = {}
        for platform in self.PLATFORM_COMMANDS.keys():
            available[platform] = self._check_command(f"agent-reach search-{platform}")
        return available
    
    def _check_command(self, cmd: str) -> bool:
        """检查命令是否可用"""
        try:
            result = subprocess.run(
                f"which {cmd.split()[0]}",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def search(self, platform: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索指定平台
        
        Args:
            platform: 平台名称
            query: 搜索关键词
            limit: 结果数量
        
        Returns:
            List[Dict]: 搜索结果列表
        """
        if platform not in self.PLATFORM_COMMANDS:
            raise ValueError(f"不支持的平台: {platform}")
        
        if not self.available_platforms.get(platform, False):
            raise RuntimeError(f"平台 {platform} 未配置或不可用")
        
        cmd = f"{self.PLATFORM_COMMANDS[platform]} '{query}' -n {limit}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"命令执行失败: {result.stderr}")
            
            return self._parse_search_results(result.stdout, platform)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("搜索超时")
        except Exception as e:
            raise RuntimeError(f"搜索失败: {str(e)}")
    
    def read_url(self, platform: str, url: str) -> Dict[str, Any]:
        """
        读取指定 URL 的内容
        
        Args:
            platform: 平台名称
            url: 目标 URL
        
        Returns:
            Dict: 内容数据
        """
        cmd = f"agent-reach read '{url}'"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"读取失败: {result.stderr}")
            
            return {
                "url": url,
                "platform": platform,
                "content": result.stdout,
                "metadata": {}
            }
            
        except Exception as e:
            return {
                "url": url,
                "platform": platform,
                "content": None,
                "metadata": {"error": str(e)}
            }
    
    def _parse_search_results(self, output: str, platform: str) -> List[Dict[str, Any]]:
        """解析搜索结果"""
        results = []
        lines = output.strip().split('\n')
        
        current_item = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配标题行 (数字. 开头)
            title_match = re.match(r'^\d+\.\s*(.+)', line)
            if title_match:
                if current_item:
                    results.append(current_item)
                current_item = {
                    "title": title_match.group(1),
                    "platform": platform,
                    "url": "",
                    "content": ""
                }
            # 匹配链接行
            elif line.startswith('🔗'):
                url = line.replace('🔗', '').strip()
                if current_item:
                    current_item["url"] = url
            # 其他内容
            elif current_item and not line.startswith('---'):
                if current_item.get("content"):
                    current_item["content"] += "\n" + line
                else:
                    current_item["content"] = line
        
        if current_item:
            results.append(current_item)
        
        return results
    
    def get_available_platforms(self) -> List[str]:
        """获取可用的平台列表"""
        return [p for p, available in self.available_platforms.items() if available]
