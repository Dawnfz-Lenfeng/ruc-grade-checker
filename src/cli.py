import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import Config
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


@app.command()
def main(
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="输出文件路径 (支持 .xlsx 和 .csv 格式)",
    ),
    no_display: bool = typer.Option(
        False,
        "--no-display",
        help="不显示成绩表格",
    ),
    browser: str = typer.Option(
        DEFAULT_BROWSER,
        "--browser",
        help="选择浏览器类型",
        show_choices=True,
    ),
    print_pdf: bool = typer.Option(
        False,
        "--print",
        help="下载成绩单PDF文件",
    ),
    download_dir: Path | None = typer.Option(
        None,
        "--download-dir",
        help="指定PDF下载目录 (默认: 当前目录)",
    ),
    wait: int = typer.Option(
        2,
        "--wait",
        help="页面加载等待时间（秒），网络不好时可以适当增加",
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="重置登录状态，清除保存的登录信息",
    ),
):
    """查询成绩并可选保存为文件"""
    if browser not in SUPPORTED_BROWSERS:
        console.print(f"[red]错误：不支持的浏览器类型 {browser}[/red]")
        raise typer.Exit(1)

    # 处理重置请求
    if reset:
        if Config.COOKIES_FILE.exists():
            Config.COOKIES_FILE.unlink()
            console.print("[green]已重置登录状态[/green]")
        else:
            console.print("[yellow]没有找到保存的登录信息[/yellow]")
        return

    # 处理下载目录
    if download_dir:
        download_dir.mkdir(parents=True, exist_ok=True)
        download_path = str(download_dir.absolute())
    else:
        download_path = os.getcwd()

    with console.status("[bold green]正在获取成绩..."):
        fetcher = GradeFetcher(browser_type=browser, wait_time=wait)
        console.print(f"使用 {browser} 浏览器获取成绩...")
        console.print(f"页面加载等待时间: {wait} 秒")

        fetcher.init_driver(headless=True, download_dir=download_path)
        grades, summary = fetcher.fetch_grades(print_pdf=print_pdf)

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

            # 显示学期总结
            if summary:
                console.print("\n[bold]学期总结：[/bold]")
                for info in summary:
                    console.print(info)

        if output:
            save_grades(grades, output)
            console.print(f"[green]成绩已保存到文件: {output}[/green]")
    else:
        console.print("[red]获取成绩失败或暂无成绩[/red]")

    if not output:
        typer.prompt("\n按回车键退出", default="", show_default=False)


if __name__ == "__main__":
    app()
