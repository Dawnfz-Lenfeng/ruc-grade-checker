# 人大教务系统成绩查询工具

一键查询成绩，支持保存为csv和xlsx格式。

## 免责声明

### 重要提示
1. 本项目仅供学习交流使用，请勿用于其他用途。使用本程序产生的任何问题由使用者**自行承担**。

2. 本项目**不提供**任何自动化功能（如定时任务），也不会对此类需求提供技术支持。此类自动化操作可能违反学校规定并导致账号被封禁。

3. 数据安全：
   - 所有数据以 JSON 格式保存在**本地**
   - 不会收集、存储或使用您的个人信息
   - 不会对您的账号进行任何未经授权的操作

4. 本项目开源且免费，作者不对以下情况负责：
   - 因使用本程序导致的账号封禁
   - 第三方对本程序的修改或滥用
   - 用户自行添加的自动化脚本导致的任何问题

### 特别说明
如果您需要自动化功能（如定时查询），请：
1. 自行评估风险
2. 遵守相关规定
3. 合理设置时间间隔
4. 对可能的后果负责

==**使用本程序即表示您已阅读并同意以上声明。**==

## 安装教程
### 环境要求
- Python 3.8 或更高版本
- Microsoft Edge 浏览器

### 安装依赖
```bash
# 克隆项目
git clone https://github.com/Dawnfz-lenfeng/ruc-grade-checker.git
cd ruc-grade-checker

# 安装依赖
pip install -r requirements.txt
```

## 使用教程
```bash
# 查看成绩（显示在终端）
python query_grades.py

# 保存为 Excel 文件
python query_grades.py -o grades.xlsx

# 保存为 CSV 文件
python query_grades.py -o grades.csv

# 仅保存文件，不显示成绩
python query_grades.py -o grades.xlsx --no-display
```

注意，在首次运行时需要手动登录：
- 程序会自动打开浏览器
- 在浏览器中输入您的学号和密码，并点击记住登录状态
- 完成登录后按回车继续
- 登录信息会保存在本地，后续使用无需重复登录
