import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)


class JWUrls:
    """教务系统URL配置"""

    def __init__(self):
        self.base = "https://v.ruc.edu.cn/"
        self.jw_base = "https://jw.ruc.edu.cn/Njw2017/index.html"

        # 路由配置
        self.routes = {
            "grades": "#/student/course-score-search/",
            "course_selection": "#/student/student-choice-center/",
            # 可以添加更多路由...
        }

    def get_url(self, route_name):
        """获取完整URL"""
        if route_name in self.routes:
            return self.jw_base + self.routes[route_name]
        return self.jw_base


class JWSystem:
    """教务系统基础类"""

    def __init__(self):
        self.urls = JWUrls()
        self.driver: Optional[WebDriver] = None
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

    def login(self):
        """登录教务系统"""
        logger.info("尝试使用Cookies登录...")
        if self.load_cookies():
            return True

        logger.info("Cookies无效，需要手动登录...")
        self.init_driver(headless=False)  # 手动登录时显示浏览器窗口
        self.driver.get(self.urls.base)

        logger.info("请在浏览器窗口中手动完成登录...")
        input("完成登录后按回车继续...")

        if self._check_login_success():
            return self.save_cookies()

        return False

    def load_cookies(self) -> bool:
        """从文件加载cookies"""
        if not os.path.exists(self.cookies_file):
            return False

        with open(self.cookies_file, "r") as f:
            cookies = json.load(f)

        self.driver.get(self.urls.base)
        self.driver.delete_all_cookies()

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get(self.urls.base)
        time.sleep(1)

        return self._check_login_success()

    def save_cookies(self) -> bool:
        """保存cookies到文件"""
        cookies = self.driver.get_cookies()

        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f)
        logger.info("Cookies已保存")

        self.init_driver(headless=True)
        return self.login()

    def navigate(self, route: str):
        """导航到指定页面"""
        target_url = self.urls.get_url(route)
        self.driver.get(target_url)

        time.sleep(1)
        current_url = self.driver.current_url

        if self.urls.routes[route] not in current_url:
            logger.info("被重定向到主页，等待应用初始化...")
            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "el-loading-spinner"))
            )
            self.driver.get(target_url)

        return self._check_navigate_success()

    def _check_login_success(self):
        """检查是否登录成功"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-logo"))
            )
            logger.info("登录成功")
            return True
        except Exception:
            logger.error("登录失败")
            return False

    def _check_navigate_success(self):
        """检查是否导航成功"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "el-menu"))
            )
            logger.info("导航成功")
            return True
        except Exception:
            logger.error("导航失败")
            return False

    def __del__(self):
        """确保关闭浏览器"""
        if self.driver:
            self.driver.quit()


@dataclass
class Grade:
    """成绩数据类"""

    course_name: str
    teacher: str
    course_type: str
    course_module: str
    credit: str
    usual_grade: str
    midterm_grade: str
    final_grade: str
    total_grade: str
    gpa: str
    note: str


class GradeFetcher(JWSystem):
    """成绩查询类"""

    def fetch_grades(self):
        """获取成绩信息"""
        try:
            if not self.driver:
                self.init_driver()

            if not self.login():
                raise Exception("登录失败")

            if not self.navigate("grades"):
                raise Exception("无法访问成绩页面")

            return self.parse_grades()

        except Exception as e:
            logger.error(f"获取成绩失败: {str(e)}")
            return []

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def parse_grades(self):
        """解析成绩数据"""
        time.sleep(1)
        table = self.driver.find_element(By.CLASS_NAME, "table-border")
        rows = table.find_elements(By.TAG_NAME, "tr")

        grades = []
        for row in rows[1:]:  # 跳过表头
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 11:
                grade = Grade(*map(lambda x: x.text.strip(), cells))
                grades.append(grade)

        logger.info(f"成功解析 {len(grades)} 条成绩记录")
        return grades
