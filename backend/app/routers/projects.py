from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth
from app.parser import scan_code

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = models.Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=List[schemas.ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return

@router.post("/{project_id}/upload")
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Only UTF-8 encoded text files are supported")

    # Check if file already exists in project
    db_file = db.query(models.ProjectFile).filter(
        models.ProjectFile.project_id == project_id,
        models.ProjectFile.filename == file.filename
    ).first()

    if db_file:
        db_file.content = content
    else:
        db_file = models.ProjectFile(
            project_id=project_id,
            filename=file.filename,
            content=content
        )
        db.add(db_file)
    
    db.commit()
    db.refresh(db_file)

    # Perform AST parsing dynamically to return response
    parsed_results = scan_code(content)
    
    return {
        "file": {
            "id": db_file.id,
            "filename": db_file.filename,
            "created_at": db_file.created_at
        },
        "analysis": parsed_results
    }

@router.get("/{project_id}/files", response_model=List[schemas.ProjectFileResponse])
def get_project_files(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return project.files

@router.get("/{project_id}/files/{file_id}/content")
def get_file_content(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify project and file ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    file_obj = db.query(models.ProjectFile).filter(
        models.ProjectFile.id == file_id,
        models.ProjectFile.project_id == project_id
    ).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    return {"filename": file_obj.filename, "content": file_obj.content}

@router.get("/{project_id}/structure")
def get_project_structure(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    structure = {}
    for file_obj in project.files:
        parsed = scan_code(file_obj.content)
        structure[file_obj.filename] = {
            "file_id": file_obj.id,
            "classes": parsed.get("classes", []),
            "functions": parsed.get("functions", []),
            "imports": parsed.get("imports", [])
        }
    return structure
