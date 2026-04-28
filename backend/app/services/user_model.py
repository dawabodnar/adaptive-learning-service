"""
Модель користувача — обʼєднує BKT для відстеження знань
по концептах і взаємодію з базою даних.
"""
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from app.models import BKTParameter, KnowledgeState, SessionTask, Task, TaskConcept
from app.services.bkt import BKTParams, update_knowledge


def get_or_create_knowledge_state(
    db: Session, user_id: int, concept_id: int
) -> KnowledgeState:
    """Повертає поточний KnowledgeState або створює новий з p_l0."""
    state = (
        db.query(KnowledgeState)
        .filter_by(user_id=user_id, concept_id=concept_id)
        .first()
    )

    if state is None:
        params = _get_bkt_params(db, concept_id)
        state = KnowledgeState(
            user_id=user_id,
            concept_id=concept_id,
            p_known=params.p_l0,
        )
        db.add(state)
        db.commit()
        db.refresh(state)

    return state


def _get_bkt_params(db: Session, concept_id: int) -> BKTParams:
    """Витягує BKT-параметри для концепту з БД, або повертає значення за замовчуванням."""
    row = db.query(BKTParameter).filter_by(concept_id=concept_id).first()
    if row is None:
        return BKTParams()
    return BKTParams(p_l0=row.p_l0, p_t=row.p_t, p_g=row.p_g, p_s=row.p_s)


def update_after_answer(
    db: Session,
    user_id: int,
    task_id: int,
    is_correct: bool,
) -> list[KnowledgeState]:
    """
    Оновлює стан знань користувача по всіх концептах,
    що перевіряються конкретним завданням.

    Повертає список оновлених KnowledgeState.
    """
    task_concepts: Iterable[TaskConcept] = (
        db.query(TaskConcept).filter_by(task_id=task_id).all()
    )

    updated_states = []
    for tc in task_concepts:
        state = get_or_create_knowledge_state(db, user_id, tc.concept_id)
        params = _get_bkt_params(db, tc.concept_id)

        new_p = update_knowledge(state.p_known, is_correct, params)
        state.p_known = new_p
        state.last_updated = datetime.now(timezone.utc)

        updated_states.append(state)

    db.commit()
    return updated_states


def get_knowledge_vector(db: Session, user_id: int) -> dict[int, float]:
    """
    Повертає вектор знань користувача по всіх концептах:
    {concept_id: p_known}
    """
    states = db.query(KnowledgeState).filter_by(user_id=user_id).all()
    return {s.concept_id: s.p_known for s in states}