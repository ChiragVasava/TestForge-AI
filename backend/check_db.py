import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Project, ProjectFile, GeneratedTest, TestRun, TestCase, TestData

db = SessionLocal()
try:
    print("--- PROJECTS ---")
    projects = db.query(Project).all()
    print(f"Total Projects: {len(projects)}")
    for p in projects:
        print(f"  Project ID: {p.id}, Name: {p.name}")
        
    print("\n--- TEST CASES ---")
    cases = db.query(TestCase).all()
    print(f"Total Test Cases: {len(cases)}")
    for c in cases:
        print(f"  Case ID: {c.id}, Project ID: {c.project_id}, Title: {c.title}")
        print(f"    Steps: {c.steps}")
        print(f"    Expected: {c.expected_result}")
        print(f"    Data: {c.test_data}")
        print("-" * 30)

    print("\n--- TEST DATA VARIABLES ---")
    data = db.query(TestData).all()
    print(f"Total variables: {len(data)}")
    for d in data:
        print(f"  Data ID: {d.id}, Project ID: {d.project_id}, Key: {d.key}, Value: {d.value}")
        
    print("\n--- TEST RUNS ---")
    runs = db.query(TestRun).all()
    print(f"Total Runs: {len(runs)}")
    for r in runs:
        print(f"  Run ID: {r.id}, Project ID: {r.project_id}, Status: {r.status}, Coverage: {r.coverage_percentage}%")
finally:
    db.close()
