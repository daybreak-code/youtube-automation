from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.scene import Scene
from fastapi.templating import Jinja2Templates
from pathlib import Path
import re
import jieba
import jieba.posseg as pseg

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

def extract_scene_info(text):
    """提取场景信息"""
    # 初始化结果字典
    scene_info = {
        'scene_type': '',
        'keywords': [],
        'characters': [],
        'actions': [],
        'emotions': [],
        'environment': [],
        'time_period': '',
        'weather': '',
        'props': []
    }
    
    # 使用结巴分词进行词性标注
    words = pseg.cut(text)
    
    for word, flag in words:
        # 人物提取（名词）
        if flag.startswith('n'):
            scene_info['keywords'].append(word)
            if flag == 'nr':  # 人名
                scene_info['characters'].append(word)
        
        # 动作提取（动词）
        elif flag.startswith('v'):
            scene_info['actions'].append(word)
        
        # 情感提取（形容词）
        elif flag.startswith('a'):
            scene_info['emotions'].append(word)
        
        # 环境提取（处所词）
        elif flag == 's':
            scene_info['environment'].append(word)
        
        # 道具提取（物品名词）
        elif flag == 'n':
            scene_info['props'].append(word)
    
    # 时间提取
    time_patterns = [
        r'([早中晚]上|凌晨|傍晚|黄昏|夜晚)',
        r'(\d+[点时]|\d+:\d+)',
        r'([春夏秋冬][天季])'
    ]
    
    for pattern in time_patterns:
        time_match = re.search(pattern, text)
        if time_match:
            scene_info['time_period'] = time_match.group(1)
            break
    
    # 天气提取
    weather_patterns = [
        r'(晴朗|多云|阴天|下雨|下雪|刮风|雾|霾)',
    ]
    
    for pattern in weather_patterns:
        weather_match = re.search(pattern, text)
        if weather_match:
            scene_info['weather'] = weather_match.group(1)
            break
    
    # 场景类型判断
    scene_types = {
        '室内': ['房间', '屋内', '室内', '客厅', '卧室', '办公室'],
        '室外': ['街道', '公园', '广场', '户外', '野外'],
        '特写': ['特写', '近景', '表情'],
        '远景': ['远景', '全景', '鸟瞰']
    }
    
    for type_name, keywords in scene_types.items():
        if any(keyword in text for keyword in keywords):
            scene_info['scene_type'] = type_name
            break
    
    # 清理并去重
    for key in scene_info:
        if isinstance(scene_info[key], list):
            scene_info[key] = list(set(scene_info[key]))
    
    return scene_info

@router.post("/scenes/extract")
async def extract_scene(text: str, db: Session = Depends(get_db)):
    """提取场景信息的API"""
    try:
        scene_info = extract_scene_info(text)
        return scene_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scenes")
async def create_scene(scene_data: dict, db: Session = Depends(get_db)):
    """创建场景记录"""
    scene = Scene(**scene_data)
    db.add(scene)
    db.commit()
    db.refresh(scene)
    return scene 