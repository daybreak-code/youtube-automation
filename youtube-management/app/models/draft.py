from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from ..database import Base

class VideoDraft(Base):
    __tablename__ = "video_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    script = Column(String)
    image_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    publish_account = Column(String)
    publish_status = Column(String, default="draft")
    published_at = Column(DateTime, nullable=True)
    workflow = Column(String)
    storyboard_count = Column(Integer) 