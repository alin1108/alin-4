from pydantic import BaseModel, ConfigDict
from pydantic import Field
from typing import Optional

class UserRequest(BaseModel):
    username:str
    password:str

#user_info 对应的类：基础类 + info类(id,用户名)
#用户信息基础类
class UserInfoBase(BaseModel):
    nickname:Optional[str] = Field(None,max_length=50,description="昵称")
    avatar:Optional[str] = Field(None,max_length=200,description="头像URL")
    gender:Optional[str] = Field(None,max_length=10,description="性别")
    bio:Optional[str] = Field(None,max_length=500,description="个人简介")

# info类(id,用户名)
class UserInfoResponse(UserInfoBase):
    id:int
    username:str

    model_config = ConfigDict(
        from_attributes=True,  # 允许从ORM对象属性中取值
    )

# data 数据类型
class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse = Field(...,alias="UserInfo")

    #模型类配置：
    model_config = ConfigDict(
        populate_by_name=True,   #alias与字段名兼容的参数
        from_attributes=True,   #允许从ORM对象属性中取值
    )


#更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname:Optional[str] = None
    avatar:Optional[str] = None
    gender:Optional[str] = None
    bio:Optional[str] = None
    phone:Optional[str] = None

#修改用户密码的模型类
class UserChangePasswordRequest(BaseModel):
    old_password:str = Field(...,alias="oldPassword",description="旧密码")
    new_password:str = Field(...,min_length=6,alias="newPassword",description="新密码")


