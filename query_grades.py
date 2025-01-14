import logging

from tabulate import tabulate

from jw_system import GradeFetcher

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_grades(grades):
    """格式化成绩数据为表格形式"""
    if not grades:
        return "暂无成绩数据"

    # 准备表格数据
    headers = [
        "教师",
        "课程名称",
        "课程编号",
        "学分",
        "平时成绩",
        "期中成绩",
        "期末成绩",
        "最终成绩",
        "学分绩点",
        "备注",
    ]

    rows = [
        [
            grade["teacher"],
            grade["course_name"],
            grade["course_code"],
            grade["credit"],
            grade["usual_grade"],
            grade["midterm_grade"],
            grade["final_grade"],
            grade["total_grade"],
            grade["gpa"],
            grade["note"],
        ]
        for grade in grades
    ]

    # 计算总学分和平均绩点
    total_credits = sum(
        float(grade["credit"])
        for grade in grades
        if grade["credit"].replace(".", "").isdigit()
    )
    valid_grades = [
        grade for grade in grades if grade["gpa"].replace(".", "").isdigit()
    ]
    avg_gpa = (
        sum(float(grade["gpa"]) for grade in valid_grades) / len(valid_grades)
        if valid_grades
        else 0
    )

    # 使用 tabulate 生成美观的表格
    table = tabulate(rows, headers=headers, tablefmt="grid")
    summary = f"\n总学分: {total_credits:.1f}\n平均绩点: {avg_gpa:.2f}"

    return table + summary


def main():
    try:
        # 初始化成绩获取器
        fetcher = GradeFetcher()

        # 获取成绩
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
