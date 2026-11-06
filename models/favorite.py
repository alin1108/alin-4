from datetime import datetime

from sqlalchemy import UniqueConstraint,Index,Integer,ForeignKey,DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

from models.news import News
from models.users import User

# 创建基类
class Base(DeclarativeBase):
    pass

#创建数据库模型类
class Favorite(Base):

    # 数据库表名
    __tablename__ = "favorite"

    # 创建数据库索引
    __table_args__ = (
    #UniqueConstraint唯一约束：当前新闻只能被收藏一次
    UniqueConstraint("user_id","news_id",name="user_news_unique"),
    Index("fk_favorite_news","news_id"),
    Index("fk_favorite_user","user_id")
    )


    id:Mapped[int] = mapped_column(
        Integer,
        primary_key=True,   #设置字段为主键
        autoincrement=True, #设置字段为自增字段
        comment="收藏ID"
    )
    user_id:Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id), #设置外键并关联用户表
        nullable=False, #设置字段不能为空
        comment="用户ID"
    )
    news_id:Mapped[int] =mapped_column(
        Integer,
        ForeignKey(News.id),
        nullable=False,
        comment="新闻ID"
    )
    created_at:Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="收藏时间"
    )

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"