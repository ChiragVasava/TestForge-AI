import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth
from app.parser import scan_code
from app.generator import generate_test_template, clean_module_name
from app.executor import execute_tests

router = APIRouter(prefix="/tests", tags=["Tests & Execution"])

@router.get("/{project_id}/generate")
def generate_tests_for_file(
    project_id: int,
    filename: str,
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

    file_obj = db.query(models.ProjectFile).filter(
        models.ProjectFile.project_id == project_id,
        models.ProjectFile.filename == filename
    ).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found in project")

    parsed = scan_code(file_obj.content)
    if "error" in parsed:
        raise HTTPException(status_code=400, detail=f"Cannot scan file due to: {parsed['error']}")

    test_content = generate_test_template(filename, parsed)
    
    test_filename = f"test_{clean_module_name(filename)}.py"

    return {
        "filename": test_filename,
        "content": test_content,
        "scanned_item_name": filename
    }

@router.post("/{project_id}/save", response_model=schemas.GeneratedTestResponse)
def save_generated_test(
    project_id: int,
    test_in: schemas.GeneratedTestCreate,
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

    # Check if test file already exists
    db_test = db.query(models.GeneratedTest).filter(
        models.GeneratedTest.project_id == project_id,
        models.GeneratedTest.filename == test_in.filename
    ).first()

    if db_test:
        db_test.content = test_in.content
        db_test.scanned_item_name = test_in.scanned_item_name
    else:
        db_test = models.GeneratedTest(
            project_id=project_id,
            filename=test_in.filename,
            content=test_in.content,
            scanned_item_name=test_in.scanned_item_name
        )
        db.add(db_test)
        
    db.commit()
    db.refresh(db_test)
    return db_test

@router.get("/{project_id}/generated", response_model=List[schemas.GeneratedTestResponse])
def get_generated_tests(
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
        
    return project.tests

@router.post("/{project_id}/run", response_model=schemas.TestRunResponse)
def run_project_tests(
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

    # Retrieve all files & test files
    files = [{"filename": f.filename, "content": f.content} for f in project.files]
    tests = [{"filename": t.filename, "content": t.content} for t in project.tests]

    if not files:
        raise HTTPException(status_code=400, detail="Cannot run tests: No project files uploaded")
    if not tests:
        raise HTTPException(status_code=400, detail="Cannot run tests: No tests saved for this project")

    # Execute tests synchronously in sandbox
    results = execute_tests(files, tests)

    # Combine coverage data and individual test cases list
    try:
        cov_data = json.loads(results["coverage_report"])
    except Exception:
        cov_data = {"percentage": results["coverage_percentage"], "files": {}}
        
    combined_report = {
        "coverage": cov_data,
        "test_cases": results["test_cases"]
    }

    # Save test run to DB
    test_run = models.TestRun(
        project_id=project_id,
        status=results["status"],
        passed_count=results["passed_count"],
        failed_count=results["failed_count"],
        coverage_percentage=results["coverage_percentage"],
        stdout_logs=results["stdout_logs"],
        coverage_report=json.dumps(combined_report)
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    return test_run

@router.get("/{project_id}/runs", response_model=List[schemas.TestRunResponse])
def get_test_runs(
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
        
    return db.query(models.TestRun).filter(
        models.TestRun.project_id == project_id
    ).order_by(models.TestRun.created_at.desc()).all()

@router.get("/{project_id}/runs/{run_id}", response_model=schemas.TestRunResponse)
def get_test_run(
    project_id: int,
    run_id: int,
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

    test_run = db.query(models.TestRun).filter(
        models.TestRun.id == run_id,
        models.TestRun.project_id == project_id
    ).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run report not found")

    return test_run
