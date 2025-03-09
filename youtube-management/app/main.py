from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .config import settings
from .database import engine, Base
from .routes import draft, storyboard

app = FastAPI()

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=settings.STATIC_FILES_DIR), name="static")

# 模板配置
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# 注册路由
app.include_router(draft.router)
app.include_router(storyboard.router)

# 添加根路由
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request}) 