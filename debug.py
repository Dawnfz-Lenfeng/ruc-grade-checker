import logging

from grade_fetcher import GradeFetcher

# 设置详细的日志级别
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def debug_login():
    fetcher = GradeFetcher()
    try:
        fetcher.init_driver()
        print("Driver 初始化成功")

        success = fetcher.login()
        print(f"登录结果: {success}")

        if success:
            print("尝试导航到成绩页面")
            nav_success = fetcher.navigate_to_grades()
            print(f"导航结果: {nav_success}")

            if nav_success:
                print("尝试解析成绩")
                grades = fetcher.parse_grades()
                print(f"获取到 {len(grades)} 条成绩")
                for grade in grades[:2]:  # 只打印前两条
                    print(grade)

        input("按回车键继续...")  # 让浏览器窗口保持打开

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        if fetcher.driver:
            fetcher.driver.quit()


if __name__ == "__main__":
    debug_login()
