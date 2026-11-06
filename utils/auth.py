from fastapi import Header,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users
from starlette import status

#整合 先提取Token再根据Token 查询用户，返回用户
async def get_current_user(
        authorization:str = Header(...,alias="Authorization"),
        db:AsyncSession = Depends(get_db)
):
    #Bearer xxxx
    # token = authorization.split(" ")[1]
    token = authorization.replace("Bearer ","")
    #通过封装好的方法来验证 Token的状态
    user = await users.get_user_by_token(db,token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或已过期的令牌")
    return user