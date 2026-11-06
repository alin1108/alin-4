import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from starlette import status
from models.users import User,UserToken
from datetime import datetime, timedelta
from schemas.users import UserRequest, UserUpdateRequest
from utils.security import get_hash_password,verify_password

# 根据用户名来查询数据库
async def get_user_by_username(db:AsyncSession,username:str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# 创建用户
async def create_user(db:AsyncSession,user_data:UserRequest):
    # 先密码加密处理 → add
    hashed_password = get_hash_password(user_data.password)
    # 创建一个新的基于用户模型类的实例
    user = User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  #从数据库读回最新的user
    return user

#生成Token
async def create_token(db:AsyncSession,user_id:int):
    #生成Token ＋ 设置过期时间 → 查询数据库当前用户是否有Token → 有:更新；无:添加
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()
    if user_token : #(有token)
        user_token.token = token
        user_token.expires_at = expires_at
        await db.commit()
    else:   #(没有token)
        user_token = UserToken(user_id = user_id,token = token,expires_at = expires_at)
        db.add(user_token)
        await db.commit()
        await db.refresh(user_token)    #从数据库读回最新的user_token
    return token

#验证登录密码
async def authenticate_user(db:AsyncSession,username:str,password:str):
    user = await get_user_by_username(db,username)
    #验证用户是否存在
    if user is None:
        return None
    #验证密文和明文是否一致
    if verify_password(password,user.password) is False:
        return None
    return user

#根据Token查询用户 ：验证Token和Token的过期时间 → 查询用户
async def get_user_by_token(db:AsyncSession,token:str):
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    # 验证Token是否存在或着Token是否过期
    if db_token is None or db_token.expires_at < datetime.now():
        return None

    # 查询用户
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#更新用户信息：update更新→检查是否命中→获取更新后的用户→返回数据
async def update_user(db:AsyncSession,username:str,user_data:UserUpdateRequest):
    #现在的user_data是Pydantic类型,得到字典 → **解包
    #没有设置值的不更新
    stmt = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    #执行ORM语句
    result = await db.execute(stmt)
    await db.commit()   #显式提交

    #判断语句是否命中了数据库
    if result.rowcount == 0 :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="用户不存在")

    #获取更新后的用户
    updated_user = await get_user_by_username(db,username)
    return updated_user

#修改用户密码：验证旧密码 → 新密码加密 →修改密码
async def change_password(db:AsyncSession,user:User,old_password:str,new_password:str):
    if not verify_password(old_password,user.password):
        return False
    hashed_new_pwd = get_hash_password(new_password)
    user.password = hashed_new_pwd
    #更新：由SQLAlchemy真正接管这个User对象，确保可以commit
    #规避session过期或关闭不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True















