from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.draft import VideoDraft
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/drafts")
async def list_drafts(request: Request, db: Session = Depends(get_db)):
    drafts = db.query(VideoDraft).all()
    return templates.TemplateResponse("drafts/list.html", {
        "request": request,
        "drafts": drafts
    })

@router.post("/drafts")
async def create_draft(draft_data: dict, db: Session = Depends(get_db)):
    draft = VideoDraft(**draft_data)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft 