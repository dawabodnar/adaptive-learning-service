"""Ендпоїнти для викладача — статистика студентів і прогрес."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import (
    Concept,
    KnowledgeState,
    LearningSession,
    SessionTask,
    User,
)

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/students")
def list_students(
    _: User = Depends(require_role("teacher", "system_admin")),
    db: Session = Depends(get_db),
):
    """Список усіх студентів із підсумковою статистикою та слабкими темами."""
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()

    result = []
    for s in students:
        sessions = db.query(LearningSession).filter(LearningSession.user_id == s.id).all()
        session_ids = [sess.id for sess in sessions]

        all_st = (
            db.query(SessionTask)
            .filter(SessionTask.session_id.in_(session_ids))
            .all()
            if session_ids else []
        )

        answered = [r for r in all_st if r.is_correct is not None]
        correct = sum(1 for r in answered if r.is_correct)
        accuracy = round(correct / len(answered), 4) if answered else 0.0

        # Слабкі концепти — де p_known < 0.5
        weak_states = (
            db.query(KnowledgeState, Concept.name)
            .join(Concept, KnowledgeState.concept_id == Concept.id)
            .filter(KnowledgeState.user_id == s.id)
            .filter(KnowledgeState.p_known < 0.5)
            .all()
        )
        weak_concepts = [c_name for _, c_name in weak_states]

        result.append({
            "id": s.id,
            "email": s.email,
            "full_name": s.full_name,
            "total_sessions": len(sessions),
            "total_answered": len(answered),
            "accuracy": accuracy,
            "weak_concepts": weak_concepts,
        })

    return result


@router.get("/students/{user_id}/progress")
def student_progress(
    user_id: int,
    _: User = Depends(require_role("teacher", "system_admin")),
    db: Session = Depends(get_db),
):
    """Детальний прогрес конкретного студента — профіль знань і сесії."""
    student = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not student:
        raise HTTPException(404, "Студента не знайдено")

    states = (
        db.query(KnowledgeState, Concept.name)
        .join(Concept, KnowledgeState.concept_id == Concept.id)
        .filter(KnowledgeState.user_id == user_id)
        .all()
    )
    knowledge_profile = [
        {
            "concept_id": s.concept_id,
            "concept_name": name,
            "p_known": round(s.p_known, 4),
        }
        for s, name in states
    ]

    sessions = (
        db.query(LearningSession)
        .filter(LearningSession.user_id == user_id)
        .order_by(LearningSession.started_at.desc())
        .limit(20)
        .all()
    )

    sessions_data = []
    for s in sessions:
        st_rows = db.query(SessionTask).filter_by(session_id=s.id).all()
        answered = [r for r in st_rows if r.is_correct is not None]
        correct = sum(1 for r in answered if r.is_correct)
        accuracy = round(correct / len(answered), 4) if answered else 0.0

        sessions_data.append({
            "session_id": s.id,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "finished_at": s.finished_at.isoformat() if s.finished_at else None,
            "total_tasks": len(st_rows),
            "answered": len(answered),
            "correct": correct,
            "accuracy": accuracy,
        })

    return {
        "student": {
            "id": student.id,
            "email": student.email,
            "full_name": student.full_name,
        },
        "knowledge_profile": knowledge_profile,
        "sessions": sessions_data,
    }