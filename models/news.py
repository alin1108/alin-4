from sqlalchemy.orm import DeclarativeBase, Mapped ,mapped_column
from datetime import datetime
from sqlalchemy import DateTime, String, Integer, Text, ForeignKey,Index
from typing import Optional

# 基类
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,   #数据库字段类型
        default = datetime.now, #默认值
        comment = "创建时间"  # 字段描述
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = datetime.now,
        comment = "更新时间"
    )

#新闻分类模型类
class Category(Base):
    __tablename__ = "news_category" #数据库表名
    id: Mapped[int] = mapped_column(
        Integer,    #字段数据类型
        primary_key =True,   #设置该字段为主键
        autoincrement = True,     #设置该字段自增
        comment = "分类id"
    )
    name: Mapped[str] = mapped_column(
        String(50),   #字段数据类型
        unique = True,    #设置字段唯一
        nullable = False,    #设置字段不能为空
        comment = "分类名称"
    )
    sort_order:Mapped[int] = mapped_column(
        Integer,
        default = 0,
        nullable = False,
        comment = "排序"
    )
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"

#新闻列表模型类
class News(Base):
    __tablename__ = "news"  #数据库表名

    #创建索引：提升查询效率 → 添加目录
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),   #高频查询场景
        Index('idx_publish_time', 'publish_time')       #按发布时间排序
    )
    id:Mapped[int] = mapped_column(
        Integer,
        primary_key = True,     #设置该字段为主键
        autoincrement= True,   #设置字段自增
        comment="新闻ID"
    )
    title:Mapped[str] = mapped_column(
        String(255),
        nullable = False,#设置字段不能为空
        comment = "新闻标题"
    )
    description:Mapped[str] = mapped_column(
        String(500),
        comment = "新闻简介"
    )
    content:Mapped[str] = mapped_column(
        Text,   #字段数据类型
        nullable = False,
        comment = "新闻内容"
    )
    image:Mapped[Optional[str]] = mapped_column(
        String(255),
        comment = "封面图片URL"
    )
    author:Mapped[Optional[str]] = mapped_column(
        String(50),
        comment = "作者"
    )
    category_id:Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news_category.id"),
        comment = "分类ID"
    )
    views:Mapped[int] = mapped_column(
        Integer,
        default = 0,
        nullable = False,
        comment = "浏览量"
    )
    publish_time:Mapped[datetime] = mapped_column(
        DateTime,
        default = datetime.now,
        comment = "发布时间"
    )
    def __repr__(self):
        return f"<News(id={self.id}, title={self.title}, views={self.views})>"
