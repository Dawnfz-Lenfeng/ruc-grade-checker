import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import config
from .jw_system import GradeFetcher
from .utils import calculate_average, save_grades

app = typer.Typer(
    name="grade-checker",
    help="人大教务系统成绩查询工具",
    add_completion=False,
)

console = Console()

SUPPORTED_BROWSERS = ["edge", "chrome"]
DEFAULT_BROWSER = "chrome"


def validate_browser(browser: str):
    if browser not in SUPPORTED_BROWSERS:
        console.print(f"[red]错误：不支持的浏览器类型 {browser}[/red]")
        raise typer.Exit(1)
    return browser


@app.command(name="show")
def show_grades(
    browser: str = typer.Option(
        DEFAULT_BROWSER,
        "--browser",
        "-b",
        help="选择浏览器类型",
        callback=validate_browser,
    ),
    wait: int = typer.Option(
        2,
        "--wait",
        "-w",
        help="页面加载等待时间（秒）",
    ),
    no_display: bool = typer.Option(
        False,
        "--no-display",
        help="不显示成绩表格",
    ),
):
    """查看成绩"""
    with console.status("[bold green]正在获取成绩..."):
        fetcher = GradeFetcher(browser_type=browser, wait_time=wait)
        fetcher.init_driver(headless=True)
        grades, summary = fetcher.fetch_grades()

    if not grades.empty:
        if not no_display:
            # 创建成绩表格
            table = Table(title="成绩查询结果")
            for col in grades.columns:
                table.add_column(col)

            for _, row in grades.iterrows():
                table.add_row(*[str(x) for x in row])

            console.print(table)

            # 显示加权平均分
            weighted_avg = calculate_average(grades)
            console.print(f"\n[bold green]学分加权平均分：{weighted_avg}[/bold green]")

            if summary:
                console.print("\n[bold]学期总结：[/bold]")
                for info in summary:
                    console.print(info)


@app.command(name="save")
def save_to_file(
    output: Path = typer.Argument(
        ...,
        help="输出文件路径 (支持 .xlsx 和 .csv 格式)",
    ),
    browser: str = typer.Option(
        DEFAULT_BROWSER,
        "--browser",
        "-b",
        help="选择浏览器类型",
        callback=validate_browser,
    ),
    wait: int = typer.Option(
        2,
        "--wait",
        "-w",
        help="页面加载等待时间（秒）",
    ),
):
    """保存成绩到文件"""
    with console.status("[bold green]正在获取成绩..."):
        fetcher = GradeFetcher(browser_type=browser, wait_time=wait)
        fetcher.init_driver(headless=True)
        grades, _ = fetcher.fetch_grades()

    if not grades.empty:
        save_grades(grades, output)
        console.print(f"[green]成绩已保存到文件: {output}[/green]")
    else:
        console.print("[red]获取成绩失败或暂无成绩[/red]")


@app.command(name="print")
def print_grades(
    browser: str = typer.Option(
        DEFAULT_BROWSER,
        "--browser",
        "-b",
        help="选择浏览器类型",
        callback=validate_browser,
    ),
    wait: int = typer.Option(
        2,
        "--wait",
        "-w",
        help="页面加载等待时间（秒）",
    ),
    download_dir: Path | None = typer.Option(
        None,
        "--dir",
        "-d",
        help="指定PDF下载目录 (默认: 当前目录)",
    ),
):
    """导出成绩单PDF"""
    # 处理下载目录
    if download_dir:
        download_dir.mkdir(parents=True, exist_ok=True)
        download_path = str(download_dir.absolute())
    else:
        download_path = os.getcwd()

    with console.status("[bold green]正在导出成绩单..."):
        fetcher = GradeFetcher(browser_type=browser, wait_time=wait)
        fetcher.init_driver(headless=True, download_dir=download_path)
        fetcher.fetch_grades(print_pdf=True)


@app.command(name="reset")
def reset_login():
    """重置登录状态"""
    if config.COOKIES_FILE.exists():
        config.COOKIES_FILE.unlink()
        console.print("[green]已重置登录状态[/green]")
    else:
        console.print("[yellow]没有找到保存的登录信息[/yellow]")


if __name__ == "__main__":
    app()
