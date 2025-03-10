from sqlalchemy import Column, Integer, String, Text, ForeignKey
from ..database import Base

class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("video_drafts.id"))
    content = Column(Text)  # 场景内容
    scene_type = Column(String)  # 场景类型
    keywords = Column(Text)  # 关键词
    characters = Column(Text)  # 人物
    actions = Column(Text)  # 动作
    emotions = Column(Text)  # 情感
    environment = Column(Text)  # 环境
    time_period = Column(String)  # 时间段
    weather = Column(String)  # 天气
    props = Column(Text)  # 道具 