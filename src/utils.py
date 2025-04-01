import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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


def calculate_average(df: pd.DataFrame):
    """计算加权平均分（不包括P/F类成绩）"""
    # 只选择最终成绩为数字的行
    numeric_grades = df[df["最终成绩"].str.match(r"^\d+$")].copy()
    if numeric_grades.empty:
        return 0.0

    numeric_grades["最终成绩"] = numeric_grades["最终成绩"].astype(float)
    numeric_grades["学分"] = numeric_grades["学分"].astype(float)

    # 计算加权平均分
    total_credits = numeric_grades["学分"].sum()
    weighted_sum = (numeric_grades["最终成绩"] * numeric_grades["学分"]).sum()
    weighted_avg = weighted_sum / total_credits if total_credits > 0 else 0.0

    return round(weighted_avg, 2)
