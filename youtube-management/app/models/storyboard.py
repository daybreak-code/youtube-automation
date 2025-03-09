from sqlalchemy import Column, Integer, String, ForeignKey, Text
from ..database import Base

class Storyboard(Base):
    __tablename__ = "storyboards"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("video_drafts.id"))
    order = Column(Integer)
    content = Column(Text)
    image_prompt = Column(Text)
    image_prompt_en = Column(Text)
    video_prompt = Column(Text)
    video_prompt_en = Column(Text)
    subtitle = Column(Text)
    subtitle_en = Column(Text)
    images = Column(Text)  # 存储为JSON字符串
    videos = Column(Text)  # 存储为JSON字符串 