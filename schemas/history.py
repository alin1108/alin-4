from pydantic import BaseModel,Field,ConfigDict
from schemas.base import NewsItemBase
from datetime import datetime
#添加浏览历史的请求头参数
class HistoryAddRequest(BaseModel):
    news_id:int  = Field(...,alias="newsId")

#浏览历史的类
class HistoryNewsItemResponse(NewsItemBase):
    history_id:int = Field(alias="historyId")
    view_time:datetime = Field(alias="viewTime")
    model_config = ConfigDict(
        from_attributes=True,   #允许从ORM模型获取属性值
        populate_by_name=True   #alias与字段名兼容的参数
    )
#浏览历史列表的响应体参数
class HistoryListResponse(BaseModel):
    list:list[HistoryNewsItemResponse]
    total:int
    has_more:bool = Field(alias="hasMore")
    model_config = ConfigDict(
        from_attributes=True,   #允许从ORM模型获取属性值
        populate_by_name=True   #alias与字段名兼容的参数
    )
