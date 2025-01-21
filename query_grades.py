import argparse
import logging
from pathlib import Path
import os

import pandas as pd

from jw_system import GradeFetcher

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


SUPPORTED_BROWSERS = ["edge", "chrome"]
DEFAULT_BROWSER = "chrome"


def save_grades(df: pd.DataFrame, output_path: Path) -> None:
    """保存成绩数据到文件"""
    suffix = output_path.suffix.lower()

    if suffix == ".xlsx":
        df.to_excel(output_path, index=False)
        logger.info(f"成绩已保存到 Excel 文件: {output_path}")
    elif suffix == ".csv":
        df.to_csv(output_path, index=False)
        logger.info(f"成绩已保存到 CSV 文件: {output_path}")
    else:
        logger.error(f"不支持的文件格式: {suffix}")


def main():
    parser = argparse.ArgumentParser(description="中国人民大学教务系统成绩查询工具")

    parser.add_argument(
        "-o", "--output", type=Path, help="输出文件路径 (支持 .xlsx 和 .csv 格式)"
    )
    parser.add_argument("--no-display", action="store_true", help="不显示成绩表格")
    parser.add_argument(
        "--browser",
        choices=SUPPORTED_BROWSERS,
        default=DEFAULT_BROWSER,
        help=f"选择浏览器类型 (默认: {DEFAULT_BROWSER})",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="下载成绩单PDF文件",
    )
    parser.add_argument(
        "--download-dir",
        type=Path,
        help="指定PDF下载目录 (默认: 当前目录)",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=2,
        help="页面加载等待时间（秒），网络不好时可以适当增加 (默认: 2)",
    )

    args = parser.parse_args()

    # 如果指定了下载目录，确保目录存在
    if args.download_dir:
        args.download_dir.mkdir(parents=True, exist_ok=True)
        download_dir = str(args.download_dir.absolute())
    else:
        download_dir = os.getcwd()

    fetcher = GradeFetcher(browser_type=args.browser, wait_time=args.wait)
    logger.info(f"使用 {args.browser} 浏览器获取成绩...")
    logger.info(f"页面加载等待时间: {args.wait} 秒")

    # 初始化时传入下载目录
    fetcher.init_driver(headless=True, download_dir=download_dir)
    grades = fetcher.fetch_grades(print_pdf=args.print)

    if not grades.empty:
        if not args.no_display:
            print("\n成绩查询结果：")
            print(grades)

        if args.output:
            save_grades(grades, args.output)
    else:
        print("获取成绩失败或暂无成绩")

    if not args.output:
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()
