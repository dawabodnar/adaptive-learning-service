"""Ендпоїнти для навчальних сесій."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import LearningSession, SessionTask, Task, User
from app.schemas import (
    AnswerResponse,
    AnswerSubmit,
    SessionStart,
    SessionStartResponse,
    SessionStats,
    TaskOut,
)
from app.services.analyzer import analyze_session
from app.services.optimizer import solve_knapsack, total_value, total_weight
from app.services.task_pool import build_pool
from app.services.user_model import update_after_answer

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: SessionStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Формуємо пул кандидатів
    pool = build_pool(db, user_id=current_user.id)

    if not pool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У базі немає активних навчальних завдань",
        )

    # 2. Розвʼязуємо задачу про рюкзак
    selected_ids = solve_knapsack(pool, capacity=payload.time_budget_seconds)

    if not selected_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Жодне завдання не вкладається у заданий бюджет часу",
        )

    # 3. Створюємо запис навчальної сесії
    session = LearningSession(
        user_id=current_user.id,
        time_budget_seconds=payload.time_budget_seconds,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.flush()  # отримати session.id

    # 4. Привʼязуємо обрані завдання до сесії
    selected_tasks: list[Task] = []
    for order, task_id in enumerate(selected_ids):
        task = db.query(Task).get(task_id)
        if task is None:
            continue
        st = SessionTask(
            session_id=session.id,
            task_id=task_id,
            order_in_session=order,
        )
        db.add(st)
        selected_tasks.append(task)

    db.commit()
    db.refresh(session)

    # 5. Готуємо відповідь
    return SessionStartResponse(
        session_id=session.id,
        time_budget_seconds=payload.time_budget_seconds,
        total_estimated_seconds=total_weight(pool, selected_ids),
        total_utility=round(total_value(pool, selected_ids), 4),
        tasks=[TaskOut.model_validate(t) for t in selected_tasks],
    )

@router.post("/{session_id}/answer", response_model=AnswerResponse)
def submit_answer(
    payload: AnswerSubmit,
    session_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Перевіряємо, що сесія існує та належить користувачу
    session = db.query(LearningSession).filter_by(id=session_id).first()
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")
    if session.finished_at is not None:
        raise HTTPException(status_code=400, detail="Сесія вже завершена")

    # Знаходимо запис session_task
    st = (
        db.query(SessionTask)
        .filter_by(session_id=session_id, task_id=payload.task_id)
        .first()
    )
    if st is None:
        raise HTTPException(
            status_code=404,
            detail="Це завдання не входить у поточну сесію",
        )
    if st.is_correct is not None:
        raise HTTPException(
            status_code=400,
            detail="На це завдання вже надано відповідь",
        )

    # Перевіряємо правильність
    task = db.query(Task).get(payload.task_id)
    is_correct = (
        payload.answer.strip().lower() == task.correct_answer.strip().lower()
    )

    # Записуємо відповідь
    st.user_answer = payload.answer
    st.is_correct = is_correct
    st.time_spent_seconds = payload.time_spent_seconds
    st.answered_at = datetime.now(timezone.utc)
    db.commit()

    # Оновлюємо модель знань (BKT)
    update_after_answer(
        db,
        user_id=current_user.id,
        task_id=payload.task_id,
        is_correct=is_correct,
    )

    return AnswerResponse(
        task_id=payload.task_id,
        is_correct=is_correct,
        submitted_answer=payload.answer,
        time_spent_seconds=payload.time_spent_seconds,
    )


@router.post("/{session_id}/finish", response_model=SessionStats)
def finish_session(
    session_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(LearningSession).filter_by(id=session_id).first()
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")
    if session.finished_at is None:
        session.finished_at = datetime.now(timezone.utc)
        db.commit()

    stats = analyze_session(db, session_id)
    return SessionStats(**stats)


@router.get("/{session_id}/stats", response_model=SessionStats)
def get_session_stats(
    session_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(LearningSession).filter_by(id=session_id).first()
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")

    stats = analyze_session(db, session_id)
    return SessionStats(**stats)
@router.get("/suggested-budget")
def get_suggested_budget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Розумний підбір бюджету часу:
    - якщо є історія завершених сесій — середня тривалість;
    - якщо ні — типове значення 30 хв.
    """
    sessions = (
        db.query(LearningSession)
        .filter(LearningSession.user_id == current_user.id)
        .filter(LearningSession.finished_at.isnot(None))
        .order_by(LearningSession.started_at.desc())
        .limit(10)
        .all()
    )

    if not sessions:
        return {
            "time_budget_seconds": 1800,
            "source": "default",
            "explanation": "Це твоя перша сесія — використовуємо стандартне значення 30 хв.",
            "based_on_sessions": 0,
        }

    # Обчислюємо середню реальну тривалість сесій
    durations = []
    for s in sessions:
        if s.finished_at and s.started_at:
            delta = (s.finished_at - s.started_at).total_seconds()
            if 60 < delta < 7200:  # відкидаємо аномалії
                durations.append(delta)

    if durations:
        avg = sum(durations) / len(durations)
    else:
        avg = sessions[0].time_budget_seconds

    # Округлення до 5 хв та обмеження
    rounded = round(avg / 300) * 300
    rounded = max(300, min(7200, rounded))

    return {
        "time_budget_seconds": int(rounded),
        "source": "history",
        "explanation": f"На основі {len(sessions)} попередніх сесій.",
        "based_on_sessions": len(sessions),
    }
@router.get("/my-history")
def get_my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Список сесій користувача з підсумковими метриками."""
    sessions = (
        db.query(LearningSession)
        .filter(LearningSession.user_id == current_user.id)
        .order_by(LearningSession.started_at.desc())
        .limit(50)
        .all()
    )

    history = []
    total_tasks = 0
    total_correct = 0
    total_seconds = 0

    for s in sessions:
        st_rows = db.query(SessionTask).filter_by(session_id=s.id).all()
        answered = [r for r in st_rows if r.is_correct is not None]
        correct = sum(1 for r in answered if r.is_correct)
        accuracy = round(correct / len(answered), 4) if answered else 0.0
        time_spent = sum(r.time_spent_seconds or 0 for r in answered)

        history.append({
            "session_id": s.id,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "finished_at": s.finished_at.isoformat() if s.finished_at else None,
            "time_budget_seconds": s.time_budget_seconds,
            "total_tasks": len(st_rows),
            "answered": len(answered),
            "correct": correct,
            "accuracy": accuracy,
            "time_spent_seconds": time_spent,
            "is_finished": s.finished_at is not None,
        })

        total_tasks += len(answered)
        total_correct += correct
        total_seconds += time_spent

    overall_accuracy = round(total_correct / total_tasks, 4) if total_tasks > 0 else 0.0

    return {
        "total_sessions": len(history),
        "total_tasks_answered": total_tasks,
        "overall_accuracy": overall_accuracy,
        "total_time_spent_seconds": total_seconds,
        "sessions": history,
    }