from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy import Index,Integer,String,Enum,DateTime,ForeignKey

#基类
class Base(DeclarativeBase):
    pass

#用户模型类
class User(Base):
    #数据库表名
    __tablename__ = "user"
    #创建数据库索引
    __table_args__ = (
        Index("username_UNIQUE","username"),
        Index("phone_UNIQUE","phone"),
    )

    #字段
    id:Mapped[int] = mapped_column(
        Integer,
        primary_key = True, #设置该字段为主键
        autoincrement = True,   #设置字段自增
        comment = "用户ID"
    )
    username:Mapped[str] = mapped_column(
        String(50),
        unique = True,    #设置字段唯一
        nullable = False,    #设置字段不能为空
        comment = "用户名"
    )
    password:Mapped[str] = mapped_column(
        String(255),
        nullable = False,
        comment = "密码(加密存储)"
    )
    nickname:Mapped[Optional[str]] = mapped_column(#选填字段
        String(50),
        comment = "昵称"
    )
    avatar:Mapped[Optional[str]] = mapped_column(#选填字段
        String(255),
        comment = "头像",
        default = "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"   #默认值
    )
    gender:Mapped[Optional[str]] = mapped_column(
        Enum("male","female","unknown"),    #性别枚举类型
        default = "unknown",    #默认值
        comment = "性别"
    )
    bio:Mapped[Optional[str]] = mapped_column(
        String(500),
        unique= True,
        comment = "个人简介",
        default = "这个人很懒，什么都没留下"
    )
    phone:Mapped[Optional[str]] = mapped_column(
        String(20),
        unique = True,
        comment = "手机号"
    )
    created_at:Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="创建时间"
    )
    updated_at:Mapped[datetime] = mapped_column(
        DateTime,
        default = datetime.now(),
        comment = "更新时间"
    )
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, nickname={self.nickname})>"

#用户令牌模型类
class UserToken(Base):
    #数据库表名
    __tablename__="user_token"
    #创建数据库索引
    __table_args__ = (
        Index("token_UNIQUE","token"),
        Index("fk_user_token_user_idx","user_id"),
    )
    id:Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="令牌ID"
    )
    user_id:Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        comment="用户ID"
    )
    token:Mapped[str] = mapped_column(
        String(255),
        unique=True,    #设置字段唯一
        nullable =False,
        comment="令牌"
    )
    expires_at:Mapped[datetime] = mapped_column(
        DateTime,
        comment="过期时间"
    )
    created_at:Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="创建时间"
    )
    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token={self.token})>"

