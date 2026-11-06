from datetime import datetime
from models.users import User
from models.news import News
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Integer,Index,ForeignKey,DateTime

#基类
class Base(DeclarativeBase):
    pass

#模型类
class History(Base):
    #数据库名
    __tablename__ = "history"
    #数据库索引
    __table_args__ = (
        Index("fk_history_user","user_id"),
        Index("fk_history_news","news_id"),
        Index("idx_view_time","view_time")
    )

    id:Mapped[int] = mapped_column(
        Integer,
        primary_key=True,   #设置字段为主键
        autoincrement=True,  #设置字段为自增
        comment="历史ID"
    )
    user_id:Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id),
        nullable=False, #设置字段不能为空
        comment="用户ID"
    )
    news_id:Mapped[int] = mapped_column(
        Integer,
        ForeignKey(News.id),
        nullable=False,
        comment="新闻ID"
    )
    view_time:Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="浏览时间"
    )
    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id},view_time={self.view_time})>"


