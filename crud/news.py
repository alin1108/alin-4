from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
from models.news import Category
from models.news import News

#获取新闻分类
async def get_categories(db:AsyncSession,skip:int = 0,limit:int= 100):
    stmt = select(Category).offset(skip).limit(limit)  #分页查询的语句
    result = await db.execute(stmt)  #执行语句并存到一个变量中
    return result.scalars().all()

#按指定分类id获取新闻列表
async def get_news_list(db:AsyncSession,category_id:int,skip:int = 0,limit:int = 10):
    #查询的是指定分类下的所有新闻列表
    stmt = select(News).where(News.category_id  == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

#计算指定分类下的新闻总量
async def get_news_count(db:AsyncSession,category_id:int):
    #查询的是指定分类下的所有新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    #因为聚合查询返回一个值，不是列表，所以用scalar()方法来处理数据
    return result.scalar_one()  #只能有一个结果,否则报错，所以用scalar_one()方法

#按指定新闻id查询新闻
async def get_news_detail(db:AsyncSession,new_id:int):
    #查询的是指定新闻id的新闻字段
    stmt = select(News).where(News.id == new_id)
    result = await db.execute(stmt)
    return result.scalars().one_or_none()   #防止用户输入了不存在的id

#进入指定新闻id的详情页中 浏览量+1
async def increase_news_views(db:AsyncSession,new_id:int):
    stmt = update(News).where(News.id == new_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit() #做一个显式提交
    #更新 → 检查数据库是否真的命中了数据 →命中了返回True
    #如果更新了一条数据,那么result.rowcount的值不为0
    return result.rowcount > 0

#获取相关新闻
async def get_related_news(db:AsyncSession,new_id:int,category_id:int,limit:int = 5):
    #思路：获取指定新闻id的分类id，然后按指定分类id获取5条相关新闻列表
    #order_by(): 排序 → 按浏览量和发布时间排序
    stmt = (select(News).where(
        News.id != new_id,
        News.category_id == category_id)
        .order_by(
            News.views.desc(),  #默认为升序，所以降序要加.desc()
            News.publish_time.desc()
        ).limit(limit)) #截取前5条数据
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    #利用列表生成式，推导出核心数据，避免返回数据过多，然后再return
    #related_news 有5个新闻，我们遍历取出每个新闻，并把每个新闻的字段格式化输出
    #方便前端取值
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "views": news_detail.views,
    } for news_detail in related_news]