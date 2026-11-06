from pydantic import BaseModel, Field,ConfigDict
from schemas.base import NewsItemBase
from datetime import datetime

class FavoriteCheckResponse(BaseModel):
    is_favorite:bool =Field(...,alias="isFavorite")

#添加收藏的请求体参数
class FavoriteAddRequest(BaseModel):
    news_id:int  = Field(...,alias="newsId")

#规划两个类：一个是新闻模型类 ＋ 收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id:int = Field(alias="favoriteId")
    favorite_time:datetime = Field(alias="favoriteTime")
    model_config = ConfigDict(
            from_attributes=True,   #允许从ORM模型获取属性值
            populate_by_name=True   #alias与字段名兼容的参数
        )

#获取收藏列表的响应体参数
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,   #允许从ORM模型获取属性值
        populate_by_name=True   #alias与字段名兼容的参数
    )