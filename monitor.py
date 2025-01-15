import json
import logging
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from notification import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradeMonitor:
    def __init__(self, send_key: str, grades_file: str = "grades.json"):
        self.notification = NotificationService(send_key)
        self.grades_file = Path(grades_file)
        self.last_modified = None
        self.last_grades = None
        self.scheduler = BlockingScheduler()

    def load_grades(self) -> pd.DataFrame:
        """加载成绩数据"""
        try:
            if not self.grades_file.exists():
                return pd.DataFrame()

            current_modified = os.path.getmtime(self.grades_file)

            # 如果文件未更新，使用缓存的数据
            if self.last_modified == current_modified and self.last_grades is not None:
                return self.last_grades

            # 文件已更新，重新加载
            with open(self.grades_file, "r", encoding="utf-8") as f:
                grades_dict = json.load(f)

            self.last_modified = current_modified
            self.last_grades = pd.DataFrame(grades_dict)
            return self.last_grades

        except Exception as e:
            logger.error(f"读取成绩失败: {str(e)}")
            return pd.DataFrame()

    def check_updates(self):
        """检查成绩更新"""
        try:
            logger.info("检查成绩文件更新...")
            current_grades = self.load_grades()

            if current_grades.empty:
                logger.info("暂无成绩数据")
                return

            # 首次运行，记录当前成绩
            if self.last_grades is None:
                self.last_grades = current_grades
                logger.info("首次加载成绩数据")
                return

            # 比较新旧成绩
            if not current_grades.equals(self.last_grades):
                # 找出更新的成绩
                merged = pd.merge(
                    current_grades,
                    self.last_grades[["课程名称", "最终成绩"]],
                    on="课程名称",
                    how="left",
                    suffixes=("", "_old"),
                )

                updates = merged[
                    (merged["最终成绩_old"].isna())  # 新课程
                    | (merged["最终成绩"] != merged["最终成绩_old"])  # 成绩变化
                ]

                if not updates.empty:
                    message = self.format_notification(updates)
                    self.notification.send_notification("新成绩通知", message)
                    logger.info(f"发现 {len(updates)} 个新成绩")

                self.last_grades = current_grades
            else:
                logger.info("没有新成绩")

        except Exception as e:
            logger.error(f"检查成绩时出错: {str(e)}")

    def format_notification(self, updated_grades: pd.DataFrame) -> str:
        """格式化通知消息"""
        message = "成绩更新通知：\n\n"
        for _, grade in updated_grades.iterrows():
            message += f"课程：{grade['课程名称']}\n"
            message += f"教师：{grade['教师']}\n"
            message += f"成绩：{grade['最终成绩']}\n"
            message += f"绩点：{grade['学分绩点']}\n"
            message += "-------------------\n"
        return message

    def start(self, interval_minutes: int = 5):
        """启动监控"""
        self.scheduler.add_job(
            self.check_updates,
            "interval",
            minutes=interval_minutes,
            next_run_time=datetime.now(),
        )
        logger.info(f"开始监控成绩更新 (每 {interval_minutes} 分钟检查一次)")
        self.scheduler.start()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    SEND_KEY = os.getenv("SEND_KEY")
    GRADES_FILE = os.getenv("GRADES_FILE", "grades.json")
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "5"))

    if not SEND_KEY:
        logger.error("请设置 SEND_KEY 环境变量")
        exit(1)

    monitor = GradeMonitor(SEND_KEY, GRADES_FILE)
    monitor.start(CHECK_INTERVAL)
