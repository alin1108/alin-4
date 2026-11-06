from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete,func
from models.favorite import Favorite
from models.news import News
#检查收藏状态：当前用户是否收藏了这条新闻
async def is_news_favorite(
    db:AsyncSession,
    news_id:int,
    user_id:int
):
    stmt = select(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    result = await db.execute(stmt)
    #是否有收藏记录
    if result.scalar_one_or_none() is None:
        return False
    return True

#添加收藏
async def add_news_favorite(
        db:AsyncSession,
        news_id:int,
        user_id:int
):
    # 创建一个新的基于用户模型类的实例
    favorite = Favorite(user_id = user_id,news_id = news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 删除收藏
async def remove_news_favorite(
    db:AsyncSession,
    news_id:int,
    user_id:int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# 获取收藏列表:获取的是某个用户的收藏列表 + 分页
async def get_favorite_list(
    db:AsyncSession,
    user_id: int,
    page:int = 1,
    page_size:int = 10
):
    #总量
    total = await get_favorite_count(db,user_id)

    #获取收藏列表 - 联表查询join() + 收藏时间的排序 + 分页
    #计算跳过的记录数
    skip = (page - 1) * page_size
    #select(查询主体模型类,字段别名).join(联合查询的模型类,联合查询的条件).where(查询的条件).order_by(排序依据的字段.desc()).offset(跳过的记录数).limit(每页的记录数)
    #别名：Favorite.created_at.label("favorite_time")
    #把同名会起冲突的列起别名，避免冲突
    stmt = (select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
            .join(Favorite,Favorite.news_id == News.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip).limit(page_size))
    result = await db.execute(stmt)
    rows = result.all()
    return rows,total
"""
rows 返回的形式
[
    (新闻对象，收藏时间，收藏id)
]
"""



# 获取收藏新闻总量
async def get_favorite_count(db:AsyncSession,user_id:int):
    stmt = select(func.count(Favorite)).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one()

#清空当前用户收藏列表
async def remove_all_favorite(db:AsyncSession,user_id:int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0