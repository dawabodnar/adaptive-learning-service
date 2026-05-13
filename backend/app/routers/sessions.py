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
from datetime import timedelta
from app.services.session_utils import check_session_expired

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
    started_at = datetime.now(timezone.utc)
    duration = payload.time_budget_seconds

    session = LearningSession(
    user_id=current_user.id,
    time_budget_seconds=duration,
    started_at=started_at,
    end_time=started_at + timedelta(seconds=duration),
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
            order_in_session=order + 1,
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
        end_time=session.end_time,
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
    if check_session_expired(session, db):
        raise HTTPException(status_code=400, detail="Сеанс закінчився")
# Перевіряємо, чи не закінчився час сесії
    now = datetime.now(timezone.utc)

    if session.end_time and now > session.end_time:
       session.finished_at = now
       db.commit()

       raise HTTPException(
        status_code=400,
        detail="Час сесії завершено",
    )
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
    if check_session_expired(session, db):
        raise HTTPException(status_code=400, detail="Сеанс закінчився")

    stats = analyze_session(db, session_id)
    return SessionStats(**stats)

@router.get("/my-history")
def get_my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
        st_rows = (
            db.query(SessionTask)
            .filter(SessionTask.session_id == s.id)
            .all()
        )
        answered = [r for r in st_rows if r.is_correct is not None]
        correct = sum(1 for r in answered if r.is_correct)
        accuracy = round(correct / len(answered), 4) if answered else 0.0
        time_spent = sum(r.time_spent_seconds or 0 for r in answered)

        # для завершених — час від старту до фінішу, для незавершених — лише реальний час на завдання
        if s.finished_at and s.started_at:
            session_duration = int((s.finished_at - s.started_at).total_seconds())
        else:
            session_duration = time_spent

        history.append({
            "session_id": s.id,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "finished_at": s.finished_at.isoformat() if s.finished_at else None,
            "time_budget_seconds": s.time_budget_seconds,
            "total_tasks": len(st_rows),
            "answered": len(answered),
            "correct": correct,
            "accuracy": accuracy,
            "time_spent_seconds": session_duration,
            "is_finished": s.finished_at is not None,
        })

        total_tasks += len(answered)
        total_correct += correct
        total_seconds += time_spent  # сумарно — завжди реальний час на завдання

    overall_accuracy = round(total_correct / total_tasks, 4) if total_tasks > 0 else 0.0

    return {
        "total_sessions": len(history),
        "total_tasks_answered": total_tasks,
        "overall_accuracy": overall_accuracy,
        "total_time_spent_seconds": total_seconds,
        "sessions": history,
    }
@router.get("/{session_id}/stats", response_model=SessionStats)
def get_session_stats(
    session_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(LearningSession).filter_by(id=session_id).first()
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")
    if check_session_expired(session, db):
        raise HTTPException(status_code=400, detail="Сеанс закінчився")

    stats = analyze_session(db, session_id)
    return SessionStats(**stats)
@router.get("/suggested-budget")
def get_suggested_budget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Бюджет часу для нової сесії:
    1) історія є → середній час, витрачений на завдання у попередніх сесіях;
    2) історії немає → стартове значення з профілю користувача.
    """
    sessions = (
        db.query(LearningSession)
        .filter(LearningSession.user_id == current_user.id)
        .order_by(LearningSession.started_at.desc())
        .limit(10)
        .all()
    )

    if not sessions:
        budget = current_user.initial_time_budget_seconds or 1800
        return {
            "time_budget_seconds": budget,
            "source": "initial",
            "explanation": f"Це твоя перша сесія — використовуємо стартове значення T = {budget // 60} хв (встановлено при реєстрації).",
            "based_on_sessions": 0,
        }

    # Збираємо фактичний час, витрачений на завдання у кожній сесії
    durations = []
    for s in sessions:
        st_rows = db.query(SessionTask).filter_by(session_id=s.id).all()
        time_spent = sum(
            (r.time_spent_seconds or 0)
            for r in st_rows
            if r.is_correct is not None
        )
        if time_spent >= 30:  # хоча б півхвилини активної роботи
            durations.append(time_spent)

    if not durations:
        # Якщо жодна сесія не дала валідних даних — беремо бюджет останньої
        budget = sessions[0].time_budget_seconds
        return {
            "time_budget_seconds": int(budget),
            "source": "previous",
            "explanation": f"Використовуємо T = {int(budget) // 60} хв з попередньої сесії (даних замало для прогнозу).",
            "based_on_sessions": 0,
        }

    avg = sum(durations) / len(durations)
    rounded = max(300, min(7200, round(avg / 60) * 60))

    return {
        "time_budget_seconds": int(rounded),
        "source": "history",
        "explanation": f"На основі {len(durations)} твоїх попередніх сесій система розрахувала T = {int(rounded) // 60} хв.",
        "based_on_sessions": len(durations),
    }

@router.get("/guest/sample-tasks")
def get_guest_sample_tasks(db: Session = Depends(get_db)):
    """Повертає 3 випадкові простіші завдання для демонстрації — без авторизації."""
    from sqlalchemy import func

    tasks = (
        db.query(Task)
        .filter(Task.is_active == True)
        .filter(Task.difficulty < 0.5)  # простіші
        .order_by(func.random())
        .limit(3)
        .all()
    )

    return [
    {
        "id": t.id,
        "content": t.content,
        "correct_answer": t.correct_answer,
        "estimated_time_seconds": t.estimated_time_seconds,
        "answer_type": t.answer_type,
    }
    for t in tasks
]