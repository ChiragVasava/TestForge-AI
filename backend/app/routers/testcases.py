import csv
import io
import json
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import google.generativeai as genai

from app.database import get_db
from app import models, schemas, auth
from app.gemini import get_gemini_key

router = APIRouter(prefix="/testcases", tags=["QA Test Cases & Automation"])

@router.get("/{project_id}", response_model=List[schemas.TestCaseResponse])
def get_test_cases(
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
    return project.testcases

@router.post("/{project_id}", response_model=schemas.TestCaseResponse, status_code=status.HTTP_201_CREATED)
def create_test_case(
    project_id: int,
    testcase_in: schemas.TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    testcase = models.TestCase(
        project_id=project_id,
        title=testcase_in.title,
        description=testcase_in.description,
        steps=testcase_in.steps,
        expected_result=testcase_in.expected_result,
        test_data=testcase_in.test_data
    )
    db.add(testcase)
    db.commit()
    db.refresh(testcase)
    return testcase

@router.delete("/{project_id}/{testcase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(
    project_id: int,
    testcase_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    testcase = db.query(models.TestCase).filter(
        models.TestCase.id == testcase_id,
        models.TestCase.project_id == project_id
    ).first()
    if not testcase:
        raise HTTPException(status_code=404, detail="Test case not found")

    db.delete(testcase)
    db.commit()
    return

@router.post("/{project_id}/import")
async def import_test_cases(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
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
        raise HTTPException(status_code=400, detail="Only UTF-8 encoded CSV files are supported")

    imported_count = 0
    errors = []

    csv_reader = csv.DictReader(io.StringIO(content))
    # Required columns validation
    required_cols = {"title", "steps", "expected_result"}
    if not required_cols.issubset(csv_reader.fieldnames or []):
        raise HTTPException(
            status_code=400, 
            detail=f"CSV must contain at least the following headers: {', '.join(required_cols)}"
        )

    for idx, row in enumerate(csv_reader):
        try:
            title = row.get("title", "").strip()
            if not title:
                errors.append(f"Row {idx+1}: 'title' column cannot be empty")
                continue
                
            steps = row.get("steps", "").strip()
            if not steps:
                errors.append(f"Row {idx+1}: 'steps' column cannot be empty")
                continue

            expected_result = row.get("expected_result", "").strip()
            if not expected_result:
                errors.append(f"Row {idx+1}: 'expected_result' column cannot be empty")
                continue

            description = row.get("description", "").strip()
            test_data = row.get("test_data", "").strip()

            testcase = models.TestCase(
                project_id=project_id,
                title=title,
                description=description if description else None,
                steps=steps,
                expected_result=expected_result,
                test_data=test_data if test_data else None
            )
            db.add(testcase)
            imported_count += 1
        except Exception as e:
            errors.append(f"Row {idx+1}: {str(e)}")

    db.commit()

    return {
        "message": f"Successfully imported {imported_count} test cases.",
        "errors": errors
    }

@router.get("/{project_id}/export")
def export_test_cases(
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

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow(["title", "description", "steps", "expected_result", "test_data"])
    
    for tc in project.testcases:
        writer.writerow([
            tc.title,
            tc.description or "",
            tc.steps,
            tc.expected_result,
            tc.test_data or ""
        ])
        
    output.seek(0)
    
    filename = f"testforge_cases_project_{project_id}.csv"
    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/{project_id}/generate-automation/{testcase_id}")
def generate_automation_script(
    project_id: int,
    testcase_id: int,
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

    testcase = db.query(models.TestCase).filter(
        models.TestCase.id == testcase_id,
        models.TestCase.project_id == project_id
    ).first()
    if not testcase:
        raise HTTPException(status_code=404, detail="Test case not found")

    # Gather test data context to inject
    test_data_items = db.query(models.TestData).filter(
        models.TestData.project_id == project_id
    ).all()
    
    data_context = {}
    for item in test_data_items:
        data_context[item.key] = item.value

    api_key = get_gemini_key()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured. Configure GEMINI_API_KEY in backend/.env"
        )

    try:
        genai.configure(api_key=api_key)
        
        # Clean title for test function
        clean_title = "".join([c if c.isalnum() else "_" for c in testcase.title.lower()])
        
        prompt = f"""
You are an expert QA and test automation engineer.
Convert the following manual test case into a working, high-quality Playwright Python script.

Test Case Details:
- Title: {testcase.title}
- Description: {testcase.description or 'No description provided'}
- Steps:
{testcase.steps}
- Expected Result: {testcase.expected_result}

Externalized Test Data Context (inject these variables if they exist in the steps/test case or use them as script parameters):
{json.dumps(data_context, indent=2)}

Your response must be the raw python code using the playwright sync or async API.
Follow these rules:
1. Include imports: `from playwright.sync_api import sync_playwright, expect` and `import os`.
2. Set up a standard run function or pytest function like `def test_{clean_title}():`.
3. Use realistic Page/Element locators, action methods (`goto`, `fill`, `click`), and assertions (`expect(element).to_be_visible()`).
4. Read externalized parameters from environment variables or defined config dictionaries if they are part of the external test data. E.g., `url = os.getenv("BASE_URL", "{data_context.get('BASE_URL', 'http://localhost:3000')}")`.
5. Output ONLY valid, executable Python code. Do not wrap it in markdown code blocks like ```python ... ``` or ```. Do not add any text before or after the code.
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Strip markdown blocks if AI returned them
        if text.startswith("```python"):
            text = text[9:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return {"script": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

# Test Data Management routes
@router.get("/{project_id}/testdata", response_model=List[schemas.TestDataResponse])
def get_test_data(
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
    return project.testdata

@router.post("/{project_id}/testdata", response_model=schemas.TestDataResponse)
def create_or_update_test_data(
    project_id: int,
    data_in: schemas.TestDataCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if key already exists
    db_data = db.query(models.TestData).filter(
        models.TestData.project_id == project_id,
        models.TestData.key == data_in.key
    ).first()

    if db_data:
        db_data.value = data_in.value
        db_data.description = data_in.description
    else:
        db_data = models.TestData(
            project_id=project_id,
            key=data_in.key,
            value=data_in.value,
            description=data_in.description
        )
        db.add(db_data)

    db.commit()
    db.refresh(db_data)
    return db_data

@router.delete("/{project_id}/testdata/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_data(
    project_id: int,
    data_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_data = db.query(models.TestData).filter(
        models.TestData.id == data_id,
        models.TestData.project_id == project_id
    ).first()
    if not db_data:
        raise HTTPException(status_code=404, detail="Test data parameter not found")

    db.delete(db_data)
    db.commit()
    return
