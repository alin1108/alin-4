from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库连接
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, # 数据库连接地址
    echo = True, # 输出SQL日志
    pool_size = 10, # 连接池大小
    max_overflow = 20, # 设置连接池允许创建的额外连接数
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind = async_engine, # 绑定异步引擎
    class_ = AsyncSession,  #设置会话类
    expire_on_commit= False, # 设置会话结束后不关闭连接
)

#设置依赖项(获取数据库会话)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:    #没有出现错误的情况
            yield session #返回数据库会话
            await session.commit()  #提交事务
        except Exception as e:
            await session.rollback()    #出现错误时，回滚事务
            raise e #抛出错误
        finally:    #无论如何都执行
            await session.close()  #关闭会话
