import json
import logging
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config import Config

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

    def __init__(self, browser_type="edge"):
        self.urls = JWUrls()
        self.driver: WebDriver = None
        self.cookies_file = Config.COOKIES_FILE
        self.browser_type = browser_type.lower()

        if self.browser_type not in ["edge", "chrome"]:
            logger.warning(f"不支持的浏览器类型: {browser_type}，将使用 edge")
            self.browser_type = "edge"

    def init_driver(self, headless=True, download_dir=None):
        """初始化浏览器驱动"""
        if self.driver:
            self.driver.quit()

        # 如果没有指定下载目录，使用当前目录
        if download_dir is None:
            download_dir = os.getcwd()

        options = (
            webdriver.EdgeOptions()
            if self.browser_type == "edge"
            else webdriver.ChromeOptions()
        )
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # 设置下载目录
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )

        if self.browser_type == "edge":
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(options=options, service=service)
        elif self.browser_type == "chrome":
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(options=options, service=service)

        self.driver.implicitly_wait(10)
        self.download_dir = download_dir  # 保存下载目录路径

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


class GradeFetcher(JWSystem):
    """成绩查询类"""

    def print_grades_pdf(self):
        """点击打印按钮下载成绩单PDF"""
        try:
            # 等待打印按钮加载
            print_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(@class, 'el-button--primary')]//span[text()='打印']",
                    )
                )
            )
            print_button.click()

            logger.info(f"成绩单PDF将下载到: {self.download_dir}")
            time.sleep(2)  # 等待下载开始
            return True
        except Exception as e:
            logger.error(f"打印成绩单失败: {str(e)}")
            return False

    def fetch_grades(
        self, output_file: str = Config.GRADES_FILE, print_pdf: bool = False
    ) -> pd.DataFrame:
        """获取成绩信息"""
        try:
            if not self.driver:
                self.init_driver()

            if not self.login():
                raise Exception("登录失败")

            if not self.navigate("grades"):
                raise Exception("无法访问成绩页面")

            grades = self.parse_grades()

            if print_pdf:
                self.print_grades_pdf()

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(grades, f, ensure_ascii=False, indent=2)
            logger.info(f"成绩数据已保存到 {output_file}")

            return pd.DataFrame(grades)

        except Exception as e:
            logger.error(f"获取成绩失败: {str(e)}")
            return pd.DataFrame()

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def parse_grades(self):
        """解析成绩数据"""
        time.sleep(1)
        table = self.driver.find_element(By.CLASS_NAME, "table-border")
        rows = table.find_elements(By.TAG_NAME, "tr")

        headers = [
            header.text.strip() for header in rows[0].find_elements(By.TAG_NAME, "th")
        ]

        grades = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == len(headers):
                grade_dict = {
                    header: cell.text.strip() for header, cell in zip(headers, cells)
                }
                grades.append(grade_dict)

        logger.info(f"成功解析 {len(grades)} 条成绩记录")
        return grades
