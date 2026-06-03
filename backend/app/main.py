from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, projects, tests, ai, testcases

# Create database tables (SQLite will create a file locally)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TestForge AI API",
    description="Intelligent Test Automation & QA Platform Backend",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tests.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(testcases.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to TestForge AI API"}
