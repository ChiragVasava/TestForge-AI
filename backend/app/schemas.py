from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Project File schemas
class ProjectFileResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True

# Generated Test schemas
class GeneratedTestResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    content: str
    scanned_item_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class GeneratedTestCreate(BaseModel):
    filename: str
    content: str
    scanned_item_name: Optional[str] = None

# Test Run schemas
class TestRunResponse(BaseModel):
    id: int
    project_id: int
    status: str
    passed_count: int
    failed_count: int
    coverage_percentage: float
    stdout_logs: Optional[str] = None
    coverage_report: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# TestCase schemas
class TestCaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    steps: str
    expected_result: str
    test_data: Optional[str] = None

class TestCaseResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    steps: str
    expected_result: str
    test_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# TestData schemas
class TestDataCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class TestDataResponse(BaseModel):
    id: int
    project_id: int
    key: str
    value: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

