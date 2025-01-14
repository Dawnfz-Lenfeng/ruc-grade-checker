import json
import logging
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)


class GradeFetcher:
    def __init__(self):
        self.base_url = "https://v.ruc.edu.cn/"
        self.driver = None
        self.cookies_file = "cookies.json"

    def init_driver(self, headless=True):
        """初始化浏览器驱动"""
        if self.driver:
            self.driver.quit()

        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = webdriver.EdgeService(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(options=options, service=service)
        self.driver.implicitly_wait(10)

    def login(self) -> bool:
        """登录教务系统"""

        logger.info("尝试使用Cookies登录...")
        if self.load_cookies():
            return True

        logger.info("Cookies无效，需要手动登录...")
        self.init_driver(headless=False)  # 手动登录时需要显示浏览器
        self.driver.get(self.base_url)

        logger.info("请在浏览器窗口中手动完成登录，并点击【记住登录状态】...")
        input("完成登录后按回车继续...")

        # 验证是否登录成功
        if self._check_login_success():
            return self.save_cookies()

        return False

    def load_cookies(self):
        """从文件加载cookies"""

        if not os.path.exists(self.cookies_file):
            return False

        with open(self.cookies_file, "r") as f:
            cookies = json.load(f)

        # 先删除所有现有的cookies
        self.driver.get(self.base_url)
        self.driver.delete_all_cookies()

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        # 刷新页面使cookies生效
        self.driver.get(self.base_url)
        time.sleep(1)

        return self._check_login_success()

    def save_cookies(self):
        """保存cookies到文件"""

        cookies = self.driver.get_cookies()
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f)
        logger.info("Cookies已保存")

        # 恢复为无界面模式
        self.init_driver(headless=True)
        return self.login()

    def navigate_to_grades(self):
        """导航到成绩查询页面"""
        try:
            # 点击成绩查询菜单
            grade_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), '成绩查询')]")
                )
            )
            grade_menu.click()

            # 等待成绩表格加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "el-table"))
            )
            return True
        except Exception as e:
            logger.error(f"导航到成绩页面失败: {str(e)}")
            return False

    def parse_grades(self):
        """解析成绩数据"""
        try:
            # 等待成绩数据加载
            time.sleep(2)  # 给予额外时间确保数据加载完成

            # 获取成绩表格中的所有行
            rows = self.driver.find_elements(By.CSS_SELECTOR, ".el-table__row")

            grades = []
            for row in rows:
                columns = row.find_elements(By.CSS_SELECTOR, ".el-table__cell")
                grade_data = {
                    "course_name": columns[1].text,  # 课程名称
                    "grade": columns[4].text,  # 成绩
                    "credit": columns[2].text,  # 学分
                    "course_type": columns[3].text,  # 课程类型
                    "semester": columns[0].text,  # 学期
                }
                grades.append(grade_data)

            return grades

        except Exception as e:
            logger.error(f"解析成绩数据失败: {str(e)}")
            return []

    def fetch_grades(self):
        """获取成绩信息的主函数"""
        try:
            if not self.driver:
                self.init_driver()

            if not self.login():
                raise Exception("登录失败")

            if not self.navigate_to_grades():
                raise Exception("无法访问成绩页面")

            grades = self.parse_grades()

            logger.info(f"成功获取到 {len(grades)} 条成绩记录")
            return grades

        except Exception as e:
            logger.error(f"获取成绩失败: {str(e)}")
            return []

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _check_login_success(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-logo"))
            )
            logger.info("登录成功")
            return True
        except Exception:
            logger.error("登录失败，请确认是否正确登录")
            return False
