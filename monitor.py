import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from db import GradeDatabase
from jw_system import GradeFetcher
from notification import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradeMonitor:
    def __init__(self, send_key):
        self.notification = NotificationService(send_key)
        self.db = GradeDatabase()
        self.fetcher = GradeFetcher()
        self.scheduler = BlockingScheduler()

    def compare_grades(self, new_grades, old_grades):
        new_dict = {g["course_name"]: g for g in new_grades}
        old_dict = {g["course_name"]: g for g in old_grades}

        updates = []
        for course, new_grade in new_dict.items():
            if (
                course not in old_dict
                or new_grade["grade"] != old_dict[course]["grade"]
            ):
                updates.append(new_grade)
        return updates

    def format_notification(self, updated_grades):
        message = "成绩更新通知：\n\n"
        for grade in updated_grades:
            message += f"课程：{grade['course_name']}\n"
            message += f"成绩：{grade['grade']}\n"
            message += "-------------------\n"
        return message

    def check_grades(self):
        try:
            logger.info("开始检查成绩更新...")
            current_grades = self.fetcher.fetch_grades()
            old_grades = self.db.get_latest_grades()

            updates = self.compare_grades(current_grades, old_grades)

            if updates:
                message = self.format_notification(updates)
                self.notification.send_notification("新成绩通知", message)
                self.db.save_grades(current_grades)
                logger.info(f"发现 {len(updates)} 个新成绩")
            else:
                logger.info("没有新成绩")

        except Exception as e:
            logger.error(f"检查成绩时出错: {str(e)}")

    def start(self, interval_minutes=30):
        self.scheduler.add_job(
            self.check_grades,
            "interval",
            minutes=interval_minutes,
            next_run_time=datetime.now(),  # 立即执行一次
        )
        self.scheduler.start()


if __name__ == "__main__":
    # 从环境变量或配置文件读取这些值
    SEND_KEY = "YOUR_SEND_KEY"

    monitor = GradeMonitor(SEND_KEY)
    monitor.start()
