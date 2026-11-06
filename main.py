from fastapi import FastAPI
from routers import news
from routers import users
from routers import favorite
from routers import history
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers
from contextlib import asynccontextmanager
from config.db_conf import async_engine


#添加生命周期管理器(确保显式地 dispose 关掉数据库引擎)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行初始化逻辑
    yield
    # 应用关闭时可以添加清理逻辑
    await async_engine.dispose()#关闭数据库连接

# 将 lifespan 传递给 FastAPI 实例
app = FastAPI(lifespan=lifespan)

#注册/挂载异常处理器
register_exception_handlers(app)

#添加CORS中间件解决前后端跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],    #允许的前端源
    allow_credentials = True,    #允许携带cookie
    allow_methods = ["*"],    #允许的请求方法
    allow_headers = ["*"]   #允许的请求头(一些Token)
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

#挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
