import logging
from typing import List

from tabulate import tabulate

from jw_system import Grade, GradeFetcher

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_grades(grades: List[Grade]) -> str:
    """格式化成绩数据为表格形式"""
    if not grades:
        return "暂无成绩数据"

    # 准备表格数据
    headers = [
        "课程名称",
        "教师",
        "课程类别",
        "课程模块",
        "学分",
        "平时成绩",
        "期中成绩",
        "期末成绩",
        "最终成绩",
        "学分绩点",
        "成绩标志",
    ]

    # 使用 dataclass 的属性直接构建行数据
    rows = [
        [getattr(grade, field) for field in Grade.__dataclass_fields__]
        for grade in grades
    ]

    # 计算统计数据
    valid_grades = [g for g in grades if g.credit.replace(".", "").isdigit()]
    total_credits = sum(float(g.credit) for g in valid_grades)

    gpa_grades = [g for g in valid_grades if g.gpa.replace(".", "").isdigit()]
    avg_gpa = (
        sum(float(g.gpa) for g in gpa_grades) / sum(float(g.credit) for g in gpa_grades)
        if gpa_grades
        else 0
    )

    score_grades = [g for g in valid_grades if g.total_grade.replace(".", "").isdigit()]
    avg_score = (
        sum(float(g.credit) * float(g.total_grade) for g in score_grades)
        / sum(float(g.credit) for g in score_grades)
        if score_grades
        else 0
    )

    # 使用 tabulate 生成美观的表格
    table = tabulate(rows, headers=headers, tablefmt="grid")
    summary = (
        f"\n总学分: {total_credits:.1f}\n"
        f"加权平均分: {avg_score:.2f}\n"
        f"加权平均绩点: {avg_gpa:.2f}"
    )

    return table + summary


def main():
    try:
        fetcher = GradeFetcher()

        logger.info("正在获取成绩...")
        grades = fetcher.fetch_grades()

        if grades:
            print("\n成绩查询结果：")
            print(format_grades(grades))
        else:
            print("获取成绩失败或暂无成绩")

    except Exception as e:
        logger.error(f"查询成绩时出错: {str(e)}")
    finally:
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()
