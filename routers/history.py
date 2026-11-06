import sqlalchemy
from fastapi import APIRouter,Depends,Query,Request,Path,HTTPException
from starlette import status
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.history import HistoryAddRequest,HistoryListResponse,HistoryNewsItemResponse
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response
from crud.history import post_history,get_history_list,remove_history,remove_all_history
import crud.history
import logging


router = APIRouter(prefix="/api/history",tags=["history"])

# 添加浏览历史
@router.post("/add")
async def add_history(
        data:HistoryAddRequest,
        db:AsyncSession = Depends(get_db),
        user:User = Depends(get_current_user)
):
    result = await post_history(db,data.news_id,user.id)
    return success_response(message="添加浏览历史成功",data=result)


# 获取浏览历史列表
@router.get("/list")
async def get_history_list(
        page:int = Query(1,ge = 1),     #页码
        page_size:int = Query(10,ge = 1,le = 100,alias="pageSize"),     #每页的记录数
        user:User = Depends(get_current_user),  #认证请求头
        db:AsyncSession = Depends(get_db)
):
    rows,total = await crud.history.get_history_list(db, user.id, page, page_size)
    has_more = total > page * page_size
    history_list = [HistoryNewsItemResponse.model_validate({
         **news.__dict__,
         "view_time": view_time,
         "history_id": history_id
    }) for news, view_time, history_id in rows]
    data = HistoryListResponse(list=history_list, total=total,hasMore=has_more)
    return success_response(message="获取浏览历史列表成功", data=data)

# 删除单条浏览历史
@router.delete("/delete/{id}")
async def delete_history(
        news_id:int= Path(...,gt = 0,alias="id",description="浏览历史的新闻ID"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await remove_history(db,news_id,user.id)
    if not result:
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="浏览历史不存在")
    return success_response(message="删除浏览历史成功")

# 清空浏览历史列表
@router.delete("/clear")
async def clear_history(
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    count = await remove_all_history(db,user.id)
    return success_response(message=f"清空了{count}条浏览记录")







