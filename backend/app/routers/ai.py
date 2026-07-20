from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal

from app.database import get_db
from app import models, auth
from app.gemini import suggest_edge_cases

router = APIRouter(prefix="/ai", tags=["AI Copilot"])

class RecommendationRequest(BaseModel):
    file_id: int
    name: str
    element_type: Literal["class", "function"]

@router.post("/recommend")
def get_recommendations(
    req: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Retrieve file and verify project ownership
    file_obj = db.query(models.ProjectFile).filter(
        models.ProjectFile.id == req.file_id
    ).first()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
        
    project = db.query(models.Project).filter(
        models.Project.id == file_obj.project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Generate recommendations — pass the full file content as context so
    # Gemini understands all class definitions and import relationships
    suggestions = suggest_edge_cases(
        code=file_obj.content,
        name=req.name,
        element_type=req.element_type,
        full_file_content=file_obj.content
    )
    
    return suggestions

