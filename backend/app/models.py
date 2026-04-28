from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    knowledge_states = relationship("KnowledgeState", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)

    parent = relationship("Concept", remote_side=[id], backref="children")
    bkt_parameters = relationship("BKTParameter", back_populates="concept", uselist=False, cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    difficulty = Column(Float, default=0.0)
    discrimination = Column(Float, default=1.0)
    guessing = Column(Float, default=0.25)
    estimated_time_seconds = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    concepts = relationship("TaskConcept", back_populates="task", cascade="all, delete-orphan")


class TaskConcept(Base):
    __tablename__ = "task_concepts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    weight = Column(Float, default=1.0)

    task = relationship("Task", back_populates="concepts")
    concept = relationship("Concept")

    __table_args__ = (
        UniqueConstraint("task_id", "concept_id", name="uq_task_concept"),
    )


class KnowledgeState(Base):
    __tablename__ = "knowledge_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    p_known = Column(Float, default=0.5)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="knowledge_states")
    concept = relationship("Concept")

    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_user_concept"),
    )


class LearningSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_budget_seconds = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    session_tasks = relationship("SessionTask", back_populates="session", cascade="all, delete-orphan")


class SessionTask(Base):
    __tablename__ = "session_tasks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    order_in_session = Column(Integer, default=0)

    session = relationship("LearningSession", back_populates="session_tasks")
    task = relationship("Task")


class BKTParameter(Base):
    __tablename__ = "bkt_parameters"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, unique=True)
    p_l0 = Column(Float, default=0.3)
    p_t = Column(Float, default=0.2)
    p_g = Column(Float, default=0.2)
    p_s = Column(Float, default=0.1)

    concept = relationship("Concept", back_populates="bkt_parameters")