from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.storyboard import Storyboard
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/storyboards")
async def list_storyboards(request: Request, draft_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Storyboard)
    if draft_id:
        query = query.filter(Storyboard.draft_id == draft_id)
    storyboards = query.all()
    return templates.TemplateResponse("storyboard/list.html", {
        "request": request,
        "storyboards": storyboards,
        "projects": []  # 这里需要添加项目列表的查询
    })

@router.post("/storyboards")
async def create_storyboard(storyboard_data: dict, db: Session = Depends(get_db)):
    storyboard = Storyboard(**storyboard_data)
    db.add(storyboard)
    db.commit()
    db.refresh(storyboard)
    return storyboard

@router.put("/storyboards/{id}")
async def update_storyboard(id: int, field: str, value: str, db: Session = Depends(get_db)):
    storyboard = db.query(Storyboard).filter(Storyboard.id == id).first()
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    setattr(storyboard, field, value)
    db.commit()
    db.refresh(storyboard)
    return storyboard 