from fastapi import APIRouter, HTTPException
from crud import news
from fastapi import Depends,Query
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news_cache

#创建APIRouter 实例
router = APIRouter(prefix="/api/news",tags=["news"])

#获取新闻分类
@router.get("/categories")
async def get_categories(
        db:AsyncSession = Depends(get_db),  # 数据库会话
        skip:int = 0,   #跳过的记录数
        limit:int= 100  #返回的记录数
):
    categories = await news_cache.get_categories(db,skip,limit)
    return {
        "code":200, #状态码
        "message":"获取新闻分类成功",
        "data":categories
    }

#获取新闻列表
@router.get("/list")
async def get_news(
        category_id:int = Query(...,alias="categoryId"),#新闻分类id
        page:int = 1,   #页码
        page_size:int = Query(10,le = 100,alias="pageSize"),#每页的记录数
        db:AsyncSession = Depends(get_db)
):
    #思路：处理分页规则 → 查询新闻列表 → 计算总量 → 计算是否还有更多(跳过的记录数+当前新闻列表的记录数<当前分类id的新闻总量)
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db,category_id,offset,page_size)
    total = await news.get_news_count(db,category_id)
    has_more = (offset + len(news_list)) < total
    return {
        "code":200,
        "message":"获取新闻列表成功",
        "data": {
        "list":news_list,
        "total":total,    #当前分类下新闻的总记录数
        "hasMore": has_more #前端页面篇幅有限,新闻太多时,参数为True时,则可以滑动加载更多
        }
    }

# 获取新闻详情
@router.get("/detail")
async def get_news_detail(
    db:AsyncSession = Depends(get_db),
    new_id:int=Query(...,alias="id")
):
    #思路：获取新闻详情 + 浏览量+1 + 相关新闻
    #获取新闻详情
    news_detail = await news.get_news_detail(db,new_id)
    if news_detail is None:
        raise HTTPException(status_code = 404,detail = "新闻不存在")
    #浏览量+1
    views_res = await news.increase_news_views(db,news_detail.id)
    if views_res is False:
        raise HTTPException(status_code = 404,detail = "添加浏览量失败")
    #相关新闻
    related_news = await news.get_related_news(db,news_detail.id,news_detail.category_id)
    return {
        "code":200,
        "message":"success",
        "data":{
            "id":news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publishTime":news_detail.publish_time,
            "views":news_detail.views,
            "relatedNews":related_news
        }
    }
