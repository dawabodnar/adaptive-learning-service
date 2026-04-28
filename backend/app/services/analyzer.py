"""
Модуль аналізу результатів навчальної сесії.

Використовує pandas для агрегації результатів по концептах,
обчислення відсотка правильних відповідей, середнього часу
виконання та виявлення слабких концептів.
"""
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models import (
    Concept,
    LearningSession,
    SessionTask,
    Task,
    TaskConcept,
)


def analyze_session(db: Session, session_id: int) -> dict[str, Any]:
    """
    Повертає підсумкову статистику сесії:
    - загальні метрики (відсоток правильних, час, кількість);
    - розбивка по концептах;
    - список слабких концептів (де < 50% правильних відповідей).
    """
    # Витягуємо всі завдання сесії з відповідями
    rows = (
        db.query(
            SessionTask.task_id,
            SessionTask.is_correct,
            SessionTask.time_spent_seconds,
            Task.estimated_time_seconds,
        )
        .join(Task, SessionTask.task_id == Task.id)
        .filter(SessionTask.session_id == session_id)
        .all()
    )

    if not rows:
        return {
            "session_id": session_id,
            "total_tasks": 0,
            "answered": 0,
            "correct": 0,
            "accuracy": 0.0,
            "total_time_spent": 0,
            "avg_time_per_task": 0.0,
            "by_concept": [],
            "weak_concepts": [],
        }

    df = pd.DataFrame(rows, columns=["task_id", "is_correct", "time_spent", "estimated_time"])

    # Загальні метрики
    answered_df = df[df["is_correct"].notna()]
    total_tasks = len(df)
    answered = len(answered_df)
    correct = int(answered_df["is_correct"].sum()) if answered > 0 else 0
    accuracy = round(correct / answered, 4) if answered > 0 else 0.0
    total_time_spent = int(answered_df["time_spent"].fillna(0).sum())
    avg_time_per_task = (
        round(answered_df["time_spent"].fillna(0).mean(), 2) if answered > 0 else 0.0
    )

    # Розбивка по концептах: збираємо звʼязки task → concept
    task_ids = df["task_id"].tolist()
    tc_rows = (
        db.query(TaskConcept.task_id, TaskConcept.concept_id, Concept.name)
        .join(Concept, TaskConcept.concept_id == Concept.id)
        .filter(TaskConcept.task_id.in_(task_ids))
        .all()
    )

    by_concept = []
    weak_concepts = []
    if tc_rows:
        tc_df = pd.DataFrame(tc_rows, columns=["task_id", "concept_id", "concept_name"])
        merged = tc_df.merge(df[["task_id", "is_correct"]], on="task_id", how="left")

        # Тільки відповіді (NaN — не відповіли)
        answered_merged = merged[merged["is_correct"].notna()]

        if not answered_merged.empty:
            grouped = answered_merged.groupby(["concept_id", "concept_name"]).agg(
                tasks_count=("task_id", "count"),
                correct_count=("is_correct", "sum"),
            ).reset_index()
            grouped["accuracy"] = (grouped["correct_count"] / grouped["tasks_count"]).round(4)

            for _, row in grouped.iterrows():
                stats = {
                    "concept_id": int(row["concept_id"]),
                    "concept_name": row["concept_name"],
                    "tasks_count": int(row["tasks_count"]),
                    "correct_count": int(row["correct_count"]),
                    "accuracy": float(row["accuracy"]),
                }
                by_concept.append(stats)
                if stats["accuracy"] < 0.5:
                    weak_concepts.append(stats)

    return {
        "session_id": session_id,
        "total_tasks": total_tasks,
        "answered": answered,
        "correct": correct,
        "accuracy": accuracy,
        "total_time_spent": total_time_spent,
        "avg_time_per_task": avg_time_per_task,
        "by_concept": by_concept,
        "weak_concepts": weak_concepts,
    }