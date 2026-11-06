from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
from models.news import Category
from models.news import News
from cache.news_cache import get_cached_categories,set_cache_categories,get_cache_news_list,set_cache_news_list
from schemas.base import NewsItemBase


#获取新闻分类(缓存版)
async def get_categories(db:AsyncSession,skip:int = 0,limit:int= 100):
    #先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:   #判断缓存中有没有这些数据
        return cached_categories    #缓存中有数据，直接返回
    stmt = select(Category).offset(skip).limit(limit)  #分页查询的语句
    result = await db.execute(stmt)  #执行语句并存到一个变量中
    categories = result.scalars().all() #ORM
    #写入缓存
    if categories:   #判断查询的数据是否为空
        categories = jsonable_encoder(categories)    #将这个ORM对象序列化转换成json,也就是我们需要的数据
        await set_cache_categories(categories) #如果有数据则写入缓存
    #返回数据
    return categories

#按指定分类id获取新闻列表(缓存版)
async def get_news_list(db:AsyncSession,category_id:int,skip:int = 0,limit:int = 10):
    # 尝试从缓存获取新闻列表
    #skip:跳过的记录数，limit:每页的记录数 page:页码 = 跳过的记录数//每页的记录数 + 1
    #跳过的记录数 = 每页的记录数 * (页码 - 1)
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id,page,limit)
    if cached_list: #查询缓存中有数据，如果有就返回
        return [News(**item)for item in cached_list]    #把缓存中的查询到的json数据转换成ORM对象

    #查询的是指定分类下的所有新闻列表
    stmt = select(News).where(News.category_id  == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    #写入缓存
    if news_list:
        #先把ORM 数据 转换成字典才能写入缓存
        #ORM 转成Pydantic,再转为字典
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cache_news_list(category_id,page,limit,news_data)

    return news_list
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