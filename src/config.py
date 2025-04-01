from pathlib import Path


class Config:
    APP_DIR = Path.home() / ".ruc-grade-checker"
    APP_DIR.mkdir(parents=True, exist_ok=True)

    # Json文件路径
    COOKIES_FILE = APP_DIR / "cookies.json"
    GRADES_FILE = APP_DIR / "grades.json"


config = Config()
