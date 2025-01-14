import json
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


class GradeDatabase:
    def __init__(self, db_path="grades.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_name TEXT,
                    grade TEXT,
                    update_time TIMESTAMP,
                    raw_data TEXT
                )
            """
            )

    def save_grades(self, grades_data):
        current_time = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            for grade in grades_data:
                conn.execute(
                    """
                    INSERT INTO grades (course_name, grade, update_time, raw_data)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        grade["course_name"],
                        grade["grade"],
                        current_time,
                        json.dumps(grade),
                    ),
                )

    def get_latest_grades(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT course_name, grade, raw_data
                FROM grades
                GROUP BY course_name
                HAVING update_time = MAX(update_time)
            """
            )
            return [
                dict(zip(["course_name", "grade", "raw_data"], row))
                for row in cursor.fetchall()
            ]
