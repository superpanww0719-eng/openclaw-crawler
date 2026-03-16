"""
CLI 命令行接口
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.json import JSON as RichJSON

from ..skill import CrawlerSkill, crawl as crawl_func

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """OpenClaw Crawler - 企业级爬虫系统"""
    pass


@main.command()
@click.argument('url')
@click.option('--platform', '-p', default='auto', help='平台类型 (wechat/web/xiaohongshu/twitter等)')
@click.option('--output', '-o', default=None, help='输出文件路径')
@click.option('--format', '-f', 'output_format', default='rich', type=click.Choice(['rich', 'json', 'markdown']))
def crawl(url: str, platform: str, output: str, output_format: str):
    """
    爬取指定 URL
    
    示例:
        openclaw-crawler crawl "https://mp.weixin.qq.com/s/xxxxx" --platform wechat
    """
    console.print(f"[bold blue]正在爬取:[/bold blue] {url}")
    console.print(f"[dim]平台: {platform}[/dim]")
    
    try:
        result_json = crawl_func(url, platform)
        result = json.loads(result_json)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result_json)
            console.print(f"[green]结果已保存到: {output}[/green]")
        
        if output_format == 'json':
            console.print(RichJSON(result_json))
        elif output_format == 'markdown':
            _print_markdown(result)
        else:
            _print_rich_result(result)
            
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        raise click.Abort()


@main.command()
@click.argument('platform')
@click.argument('query')
@click.option('--limit', '-n', default=10, help='结果数量限制')
@click.option('--output', '-o', default=None, help='输出文件路径')
def search(platform: str, query: str, limit: int, output: str):
    """
    搜索指定平台
    
    示例:
        openclaw-crawler search xiaohongshu "Python教程" --limit 5
    """
    console.print(f"[bold blue]搜索 {platform}:[/bold blue] {query}")
    
    try:
        from ..skill import search as search_func
        results_json = search_func(platform, query, limit)
        results = json.loads(results_json)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(results_json)
            console.print(f"[green]结果已保存到: {output}[/green]")
        
        _print_search_results(results)
        
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        raise click.Abort()


@main.command()
@click.argument('url')
def test(url: str):
    """
    测试爬取功能（用于验证）
    
    示例:
        openclaw-crawler test "https://mp.weixin.qq.com/s/xxxxx"
    """
    console.print(f"[bold blue]测试爬取:[/bold blue] {url}")
    console.print("[dim]这将检测页面类型并尝试爬取...[/dim]\n")
    
    try:
        skill = CrawlerSkill()
        result = skill.crawl(url)
        
        table = Table(title="爬取结果")
        table.add_column("字段", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("URL", result.url)
        table.add_row("成功", "✓" if result.success else "✗")
        table.add_row("标题", result.title or "N/A")
        table.add_row("作者", result.author or "N/A")
        table.add_row("发布时间", result.publish_time or "N/A")
        
        if result.metadata and result.metadata.get('requires_captcha'):
            table.add_row("状态", "[yellow]需要验证码[/yellow]")
        
        if result.error_message:
            table.add_row("错误", f"[red]{result.error_message}[/red]")
        
        console.print(table)
        
        if result.content:
            console.print("\n[bold]内容预览:[/bold]")
            preview = result.content[:500] + "..." if len(result.content) > 500 else result.content
            console.print(preview)
        
        # 返回测试结果
        if result.success:
            console.print("\n[bold green]✓ 测试通过[/bold green]")
        else:
            console.print("\n[bold red]✗ 测试失败[/bold red]")
            
    except Exception as e:
        console.print(f"\n[bold red]✗ 测试失败: {str(e)}[/bold red]")
        raise click.Abort()


def _print_rich_result(result: dict):
    """打印美观的结果"""
    table = Table(title="爬取结果")
    table.add_column("字段", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("URL", result.get('url', 'N/A'))
    table.add_row("成功", "✓" if result.get('success') else "✗")
    table.add_row("标题", result.get('title') or "N/A")
    table.add_row("作者", result.get('author') or "N/A")
    table.add_row("发布时间", result.get('publish_time') or "N/A")
    
    metadata = result.get('metadata', {})
    if metadata.get('requires_captcha'):
        table.add_row("状态", "[yellow]需要验证码[/yellow]")
    
    if result.get('error_message'):
        table.add_row("错误", f"[red]{result['error_message']}[/red]")
    
    console.print(table)
    
    if result.get('content'):
        console.print("\n[bold]内容:[/bold]")
        console.print(result['content'][:1000])


def _print_markdown(result: dict):
    """打印 Markdown 格式"""
    md = f"""# {result.get('title', '无标题')}

**URL:** {result.get('url')}
**作者:** {result.get('author', '未知')}
**发布时间:** {result.get('publish_time', '未知')}

## 内容

{result.get('content', '无内容')}

---
*爬取自 OpenClaw Crawler*
"""
    console.print(md)


def _print_search_results(results: list):
    """打印搜索结果"""
    if not results:
        console.print("[yellow]未找到结果[/yellow]")
        return
    
    table = Table(title=f"搜索结果 ({len(results)} 条)")
    table.add_column("#", style="cyan", width=4)
    table.add_column("标题", style="green")
    table.add_column("URL", style="blue")
    
    for i, item in enumerate(results, 1):
        title = item.get('title', 'N/A')[:50]
        url = item.get('url', 'N/A')[:60]
        table.add_row(str(i), title, url)
    
    console.print(table)


if __name__ == '__main__':
    main()
