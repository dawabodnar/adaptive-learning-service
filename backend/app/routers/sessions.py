"""Ендпоїнти для навчальних сесій."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import LearningSession, SessionTask, Task, User
from app.schemas import SessionStart, SessionStartResponse, TaskOut
from app.services.optimizer import solve_knapsack, total_value, total_weight
from app.services.task_pool import build_pool

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