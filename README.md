# 人大教务系统成绩监控

自动监控人民大学教务系统成绩更新，当有新成绩发布时通过微信通知。

## 功能特点

- 自动监控成绩更新
- 使用 Server酱 推送微信通知
- 保存登录状态，无需重复登录
- 支持手动查询当前成绩
- 本地数据库存储历史成绩

## 安装说明

### 1. 环境要求

- Python 3.7+
- Microsoft Edge 浏览器
- Windows/Linux/MacOS

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

1. 获取 Server酱 SEND_KEY
   - 访问 [Server酱](https://sct.ftqq.com/)
   - 登录并获取 SEND_KEY

2. 编辑 `config.py` 文件：
```python
# Server酱配置
SEND_KEY = "YOUR_SEND_KEY"  # 替换为你的 SEND_KEY

# 监控配置
CHECK_INTERVAL = 30  # 检查间隔（分钟）
```

## 使用说明

### 首次使用

1. 运行调试程序：
```bash
python debug.py
```

2. 在打开的浏览器窗口中：
   - 输入用户名
   - 输入密码
   - 输入验证码
   - 点击登录按钮

3. 登录成功后按回车继续
4. 程序会自动保存登录状态（cookies），后续使用无需重复登录

### 查询当前成绩
```
usage: query_grades.py [-h] [-o OUTPUT] [--no-display]

中国人民大学教务系统成绩查询工具

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        输出文件路径 (支持 .xlsx 和 .csv 格式)
  --no-display          不显示成绩表格
```

```bash
python query_grades.py
```

输出示例：
```
+--------+----------------+--------+------------+--------+
| 学期   | 课程名称       | 学分   | 课程类型   | 成绩   |
+========+================+========+============+========+
| 2023-1 | 数据结构       | 3.0    | 必修       | 88     |
+--------+----------------+--------+------------+--------+
```

### 启动成绩监控

```bash
python monitor.py
```

- 程序会每隔设定时间检查成绩更新
- 发现新成绩时会通过微信推送通知
- 所有成绩记录会保存在本地数据库中

## 文件说明

- `monitor.py`: 成绩监控主程序
- `grade_fetcher.py`: 成绩获取模块
- `notification.py`: 微信通知模块
- `db.py`: 数据库操作模块
- `debug.py`: 调试工具
- `query_grades.py`: 成绩查询工具
- `config.py`: 配置文件
- `cookies.json`: 保存的登录状态

## 常见问题

### 1. 登录失败
- 确保正确输入验证码
- 检查网络连接是否正常
- 确认教务系统是否可以访问

### 2. 无法收到通知
- 检查 `config.py` 中的 SEND_KEY 是否正确
- 访问 [Server酱](https://sct.ftqq.com/) 测试 KEY 是否有效
- 确认是否正确关注了 Server酱 的微信通知

### 3. Cookie 失效
当出现以下情况时，需要重新登录：
- 提示 "Cookies已过期或无效"
- 长时间未使用
- 教务系统更新

解决方法：
1. 删除 `cookies.json` 文件
2. 重新运行 `debug.py` 进行登录

### 4. 其他问题
- 确保 Microsoft Edge 浏览器已安装
- 检查 Python 版本是否满足要求
- 确认所有依赖包安装正确

## 注意事项

1. 请勿频繁查询，建议将检查间隔设置在 30 分钟以上
2. 首次使用时一定要通过 `debug.py` 完成登录
3. 定期检查 cookies 是否有效
4. 建议先测试成绩查询功能，再启动监控程序

## 安全提示

- 本程序不会存储你的用户名和密码
- 登录信息以 cookies 形式保存在本地
- 建议定期更新 cookies

## 许可证

MIT License

## 免责声明

本项目仅供学习交流使用，请勿用于其他用途。使用本程序产生的任何问题由使用者自行承担。


