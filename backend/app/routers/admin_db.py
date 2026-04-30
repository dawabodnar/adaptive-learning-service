"""Ендпоїнти для адміністратора бази даних — керування завданнями і концептами."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import Concept, Task, TaskConcept, User

router = APIRouter(prefix="/admin/db", tags=["admin_db"])


# Pydantic-схеми
class TaskConceptIn(BaseModel):
    concept_id: int
    weight: float = 1.0


class TaskCreate(BaseModel):
    content: str = Field(min_length=3)
    correct_answer: str = Field(min_length=1)
    difficulty: float = 0.0
    discrimination: float = 1.0
    guessing: float = 0.25
    estimated_time_seconds: int = Field(ge=10, le=3600, default=60)
    concepts: list[TaskConceptIn] = []


class TaskUpdate(BaseModel):
    content: Optional[str] = None
    correct_answer: Optional[str] = None
    difficulty: Optional[float] = None
    discrimination: Optional[float] = None
    guessing: Optional[float] = None
    estimated_time_seconds: Optional[int] = None
    is_active: Optional[bool] = None


class TaskOut(BaseModel):
    id: int
    content: str
    correct_answer: str
    difficulty: float
    discrimination: float
    guessing: float
    estimated_time_seconds: int
    is_active: bool
    concept_ids: list[int]
    concept_names: list[str]


class ConceptOut(BaseModel):
    id: int
    name: str
    description: Optional[str]


# Ендпоїнти
@router.get("/concepts", response_model=list[ConceptOut])
def list_concepts(
    _: User = Depends(require_role("db_admin", "system_admin")),
    db: Session = Depends(get_db),
):
    concepts = db.query(Concept).order_by(Concept.id).all()
    return [
        ConceptOut(id=c.id, name=c.name, description=c.description)
        for c in concepts
    ]


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    _: User = Depends(require_role("db_admin", "system_admin")),
    db: Session = Depends(get_db),
):
    tasks = db.query(Task).order_by(Task.id).all()
    result = []
    for t in tasks:
        tcs = (
            db.query(TaskConcept, Concept.name)
            .join(Concept, TaskConcept.concept_id == Concept.id)
            .filter(TaskConcept.task_id == t.id)
            .all()
        )
        concept_ids = [tc.concept_id for tc, _ in tcs]
        concept_names = [name for _, name in tcs]

        result.append(TaskOut(
            id=t.id,
            content=t.content,
            correct_answer=t.correct_answer,
            difficulty=t.difficulty,
            discrimination=t.discrimination,
            guessing=t.guessing,
            estimated_time_seconds=t.estimated_time_seconds,
            is_active=t.is_active,
            concept_ids=concept_ids,
            concept_names=concept_names,
        ))
    return result


@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    _: User = Depends(require_role("db_admin", "system_admin")),
    db: Session = Depends(get_db),
):
    # Перевіряємо, що всі concept_id існують
    if payload.concepts:
        concept_ids = [c.concept_id for c in payload.concepts]
        existing = db.query(Concept.id).filter(Concept.id.in_(concept_ids)).all()
        existing_ids = {c.id for c in existing}
        missing = set(concept_ids) - existing_ids
        if missing:
            raise HTTPException(400, f"Концепти не знайдено: {missing}")

    task = Task(
        content=payload.content,
        correct_answer=payload.correct_answer,
        difficulty=payload.difficulty,
        discrimination=payload.discrimination,
        guessing=payload.guessing,
        estimated_time_seconds=payload.estimated_time_seconds,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(task)
    db.flush()

    for c in payload.concepts:
        db.add(TaskConcept(task_id=task.id, concept_id=c.concept_id, weight=c.weight))

    db.commit()
    db.refresh(task)

    concept_names = []
    if payload.concepts:
        concept_names = [
            n for (n,) in db.query(Concept.name).filter(Concept.id.in_([c.concept_id for c in payload.concepts])).all()
        ]

    return TaskOut(
        id=task.id,
        content=task.content,
        correct_answer=task.correct_answer,
        difficulty=task.difficulty,
        discrimination=task.discrimination,
        guessing=task.guessing,
        estimated_time_seconds=task.estimated_time_seconds,
        is_active=task.is_active,
        concept_ids=[c.concept_id for c in payload.concepts],
        concept_names=concept_names,
    )


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    payload: TaskUpdate,
    task_id: int = Path(..., ge=1),
    _: User = Depends(require_role("db_admin", "system_admin")),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Завдання не знайдено")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    tcs = (
        db.query(TaskConcept, Concept.name)
        .join(Concept, TaskConcept.concept_id == Concept.id)
        .filter(TaskConcept.task_id == task.id)
        .all()
    )

    return TaskOut(
        id=task.id,
        content=task.content,
        correct_answer=task.correct_answer,
        difficulty=task.difficulty,
        discrimination=task.discrimination,
        guessing=task.guessing,
        estimated_time_seconds=task.estimated_time_seconds,
        is_active=task.is_active,
        concept_ids=[tc.concept_id for tc, _ in tcs],
        concept_names=[name for _, name in tcs],
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_task(
    task_id: int = Path(..., ge=1),
    _: User = Depends(require_role("db_admin", "system_admin")),
    db: Session = Depends(get_db),
):
    """Архівує завдання (мʼяке видалення — is_active = false)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Завдання не знайдено")

    task.is_active = False
    db.commit()
    return None