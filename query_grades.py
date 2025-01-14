import logging

from tabulate import tabulate

from grade_fetcher import GradeFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_grades(grades):
    """格式化成绩数据为表格形式"""
    if not grades:
        return "暂无成绩数据"

    # 准备表格数据
    headers = ["学期", "课程名称", "学分", "课程类型", "成绩"]
    rows = [
        [
            grade["semester"],
            grade["course_name"],
            grade["credit"],
            grade["course_type"],
            grade["grade"],
        ]
        for grade in grades
    ]

    # 使用 tabulate 生成美观的表格
    return tabulate(rows, headers=headers, tablefmt="grid")


def main():
    try:
        # 初始化成绩获取器
        fetcher = GradeFetcher()

        # 获取成绩
        logger.info("正在获取成绩...")
        grades = fetcher.fetch_grades()

        if grades:
            print("\n当前成绩：")
            print(format_grades(grades))
        else:
            print("获取成绩失败或暂无成绩")

    except Exception as e:
        logger.error(f"查询成绩时出错: {str(e)}")


if __name__ == "__main__":
    main()
