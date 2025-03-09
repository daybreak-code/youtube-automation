# YouTube Shorts 管理系统

一个用于管理YouTube Shorts视频制作流程的系统，包括素材管理、视频草稿与剪辑和自动发布功能。

## 功能特点

- 视频草稿管理
- 分镜列表管理
- 素材管理
- 多环境与账号管理
- 在线视频复刻
- Comfy工作流管理
- 个人数据管理

## 技术栈

- Backend: Python FastAPI
- Template Engine: Jinja2
- Database: SQLite
- Frontend: Bootstrap 5
- JavaScript (Vanilla JS)

## 项目结构
plaintext
youtube_shorts_manager/
├── app/
│ ├── init.py
│ ├── main.py # FastAPI应用主入口
│ ├── config.py # 配置文件
│ ├── database.py # 数据库配置
│ ├── models/ # 数据模型
│ ├── routes/ # 路由处理
│ └── templates/ # HTML模板
├── static/ # 静态文件
│ ├── css/
│ └── js/
└── requirements.txt # 项目依赖

## 安装说明

1. 克隆项目

bash
git clone https://github.com/yourusername/youtube-shorts-manager.git
cd youtube-shorts-manager

2. 创建虚拟环境

bash
python -m venv venv
source venv/bin/activate # Linux/Mac

3. 安装依赖

bash
pip install -r requirements.txt

4. 运行项目

bash
uvicorn app.main:app --reload


访问 http://localhost:8000 即可使用系统

## 主要功能说明

### 视频草稿管理

- 新建视频草稿
- 选择模型、脚本、分镜数量
- 设置发布账号和工作流
- 查看草稿详情和预览成片

### 分镜列表管理

- 按项目筛选分镜
- 新增/编辑分镜内容
- 支持双击编辑表格内容
- 一键生成关键词/图片/视频
- 导出剪映草稿箱
- 发布到YouTube

## API文档

启动项目后访问 http://localhost:8000/docs 查看完整API文档。

## 开发指南

### 添加新路由

1. 在 `app/routes/` 下创建新的路由文件
2. 在 `app/main.py` 中注册路由
3. 在 `app/templates/` 下添加对应的模板文件

### 数据库模型

在 `app/models/` 下定义新的SQLAlchemy模型类。

### 前端开发

- CSS样式在 `static/css/style.css` 中定义
- JavaScript代码在 `static/js/` 目录下组织
- 模板文件使用Jinja2语法，存放在 `app/templates/` 目录

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

- 项目维护者：[Your Name]
- Email：[your.email@example.com]