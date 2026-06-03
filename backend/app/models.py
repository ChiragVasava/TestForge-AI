from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    owner = relationship("User", back_populates="projects")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    tests = relationship("GeneratedTest", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("TestRun", back_populates="project", cascade="all, delete-orphan")
    testcases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    testdata = relationship("TestData", back_populates="project", cascade="all, delete-orphan")


class ProjectFile(Base):
    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="files")


class GeneratedTest(Base):
    __tablename__ = "generated_tests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    scanned_item_name = Column(String, nullable=True)  # function/class name this test targets
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="tests")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False)  # pending, running, passed, failed
    passed_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    coverage_percentage = Column(Float, default=0.0, nullable=False)
    stdout_logs = Column(Text, nullable=True)
    coverage_report = Column(Text, nullable=True)  # Stores detailed JSON coverage stats
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="runs")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    test_data = Column(Text, nullable=True)  # JSON-formatted string for variables
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="testcases")


class TestData(Base):
    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="testdata")

