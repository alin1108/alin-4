from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete,func
from models.history import History
from models.news import News
from datetime import datetime


# 添加浏览历史
async def post_history(
    db:AsyncSession,
    news_id:int,
    user_id:int
):
    # 判断当前用户是否已经浏览过该新闻
    stmt = select(History).where(History.user_id == user_id,History.news_id == news_id)
    result = await db.execute(stmt)
    history = result.scalar_one_or_none()
    # 如果已经浏览过该新闻，则更新浏览时间
    if history:
        history.view_time = datetime.now()
        await db.commit()
    # 如果没有浏览过该新闻，则创建新的浏览历史
    else:
        history = History(user_id=user_id,news_id=news_id)  # 创建浏览历史模型类实例
        db.add(history)
        await db.commit()
        await db.refresh(history)
    return history

# 获取浏览历史列表+实现分页逻辑
async def get_history_list(
    db:AsyncSession,
    user_id:int,
    page:int = 1,
    page_size:int = 10
):
    # 浏览历史总量
    total = await get_history_count(db,user_id)
    # 跳过的记录数
    skip = (page - 1) * page_size
    # 获取浏览历史列表 - 联表查询join() + 浏览时间的排序 + 分页
    stmt = (select(News,History.view_time.label("view_time"),History.id.label("history_id"))
            .join(History,History.news_id == News.id)
            .where(History.user_id == user_id)
            .order_by(History.view_time.desc())
            .offset(skip).limit(page_size)
            )
    result = await db.execute(stmt)
    rows = result.all()
    return rows, total
"""
rows 返回的形式
[
    (新闻对象，浏览时间，浏览历史id)
]
"""

# 获取浏览历史的新闻总量
async def get_history_count(db:AsyncSession,user_id:int):
    stmt = select(func.count(History.id)).where(History.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one()

# 删除单条浏览历史
async def remove_history(db:AsyncSession,news_id:int,user_id:int):
    stmt = delete(History).where(History.user_id==user_id,History.news_id==news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# 删除所有浏览历史
async def remove_all_history(db:AsyncSession,user_id:int):
    stmt = delete(History).where(History.user_id==user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0



