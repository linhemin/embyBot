## Emby Bot 项目
本项目是一个基于 Pyrogram 的 Telegram Bot，用于管理 Emby 用户、发送邀请码、查询 Emby 资源等操作。同时集成了针对 Emby 路由服务的切换功能。项目主要通过 Python + SQLAlchemy + Pyrogram 实现。

### 功能概述
#### 用户管理：
- 根据邀请码创建 Emby 用户，并分配默认密码、默认策略等。
- 提供管理员命令禁用/解禁用户的 Emby 账号。
- 可查看用户当前信息（白名单、管理员身份、禁用状态等）。
#### 邀请码管理：
- 生成普通邀请码、白名单邀请码。
- 使用邀请码后自动更新数据库和相关标识。
#### 线路管理：
- 集成路由服务 API，允许用户在机器人对话中快速切换观影线路。
#### 其他辅助功能：
- 查看当前 Emby 影片数量。
- 限时或限量开放注册。

### 安装及运行
```bash
git clone https://github.com/embyplus/embyBot
cp .env.example .env
vim .env

python3 -m pip install -r requirements.txt
python3 app.py
```

### 配置环境变量

| 变量名	              | 说明	                                               | 示例值                        |
|-------------------|---------------------------------------------------|----------------------------|
| TIMEZONE          | 时区设置                                              | Asia/Shanghai              |
 | LOG_LEVEL         | 日志级别，可选 DEBUG / INFO / WARNING / ERROR / CRITICAL | INFO                       |
 | BOT_TOKEN         | 你的 Telegram Bot 令牌                                | 123456:ABC-DEF1234ghIkl... |
 | API_ID            | Telegram API ID（从 my.telegram.org 获取）             | 1234567                    |
 | API_HASH          | Telegram API Hash                                 | abcdef1234567890ghijklmn   |
 | TELEGRAM_GROUP_ID | Bot 要监听或管理的群组 ID，支持多群可用逗号分隔                       | -1001234567890             |
 | EMBY_URL          | Emby 服务器 URL                                      | https://your-emby-url      |
 | EMBY_API_KEY      | Emby 服务器 API Key                                  | embyapikey123              |
 | API_URL           | 路由服务 API 基础地址                                     | https://your-router-api    |
 | API_KEY           | 路由服务使用的鉴权 token，不需要则可留空                           | routerapikey123            |
 | DB_HOST           | 数据库主机名或 IP                                        | 127.0.0.1                  |
 | DB_PORT           | 数据库端口                                             | 3306                       |
 | DB_USER           | 数据库用户名                                            | root                       |
 | DB_PASS           | 数据库密码                                             | password                   |
 | DB_NAME           | 数据库名                                              | emby_bot_db                |
 | ADMIN_LIST        | Bot 管理员的 Telegram ID 列表（用逗号分隔）                    | 123456789,987654321        |

### Thanks
- [Pyrogram](https://docs.pyrogram.org/) - Telegram API for Python
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL Toolkit and Object-Relational Mapping
- [Emby服管理bot by小草](https://github.com/xiaocao666tzh/EmbyBot)