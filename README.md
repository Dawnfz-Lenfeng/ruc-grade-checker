# 人大教务系统成绩查询工具

一键查询成绩，支持保存为csv和xlsx格式。

## 免责声明

### 重要提示
1. 本项目仅供学习交流使用，请勿用于其他用途。使用本程序产生的任何问题由使用者**自行承担**。

2. 本项目**不提供**任何自动化功能（如定时任务），也不会对此类需求提供技术支持。此类自动化操作可能违反学校规定并导致账号被封禁。

3. 本项目所有数据以 JSON 格式保存在**本地**，不会收集、存储或使用您的个人信息，也不会对您的账号进行任何未经授权的操作。

### 特别说明
如果您需要自动化功能（如定时查询），请：
1. 自行评估风险
2. 遵守相关规定
3. 合理设置时间间隔
4. 对可能的后果负责

**使用本程序即表示您已阅读并同意以上声明。**

## 安装教程

```bash
# 克隆项目
git clone https://github.com/Dawnfz-lenfeng/ruc-grade-checker.git
cd ruc-grade-checker

# 安装项目
pip install .
```

## 使用说明

### 通用选项
所有命令都支持以下选项：

| 选项 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--browser` | `-b` | chrome | 浏览器类型（支持chrome/edge） |
| `--wait` | `-w` | 2 | 页面加载等待时间（秒） |

### 命令详解

#### 显示成绩
```bash
# 基本使用
grade-checker show

# 不显示成绩表格
grade-checker show --no-display
```

#### 保存成绩
```bash
# 保存为Excel
grade-checker save grades.xlsx

# 保存为CSV
grade-checker save grades.csv
```

#### 导出PDF
```bash
# 默认保存到当前目录
grade-checker print

# 指定保存目录
grade-checker print --dir ./pdf
```

#### 重置登录
```bash
# 清除保存的登录信息
grade-checker reset
```

### 首次使用说明

首次运行时需要手动登录：
- 程序会自动打开浏览器
- 在浏览器中输入您的学号和密码，并点击记住登录状态
- 登录信息会保存在本地，后续使用无需重复登录

### 常见问题

- 如果导航成功但是没有解析到成绩，大概率是因为网络问题没有加载完全，可以尝试增加等待时间（`--wait` 参数）。
- Mac 用户请使用 Chrome 浏览器，Edge 浏览器在 Mac 上可能无法正常使用。
