"""
Модуль формування пулу навчальних завдань.

Для кожного активного завдання обчислює:
- очікуваний час виконання (з БД);
- коефіцієнт навчальної користі — на основі поточного стану знань
  студента по концептах, які перевіряє завдання, та інформаційної
  функції IRT.
"""
from sqlalchemy.orm import Session

from app.models import KnowledgeState, Task, TaskConcept
from app.services.irt import IRTParams, item_information
from app.services.optimizer import KnapsackItem


def p_known_to_theta(p_known: float) -> float:
    """
    Перетворює BKT-ймовірність знання в IRT-рівень здібностей theta.

    Використовуємо логіт-перетворення: theta = ln(p / (1 - p)).
    Для p у (0, 1) дає theta у (-inf, +inf), а p = 0.5 дає theta = 0.
    """
    eps = 1e-6
    p = max(eps, min(1.0 - eps, p_known))
    import math
    return math.log(p / (1 - p))


def compute_task_utility(
    task: Task,
    knowledge_vector: dict[int, float],
    task_concepts: list[TaskConcept],
) -> float:
    """
    Навчальна користь завдання для конкретного студента.

    Логіка: користь висока, коли:
    1) концепти, що перевіряє завдання, ще не повністю засвоєні
       (тобто 1 - p_known велике);
    2) IRT-інформаційна функція в поточній точці theta велика
       (завдання інформативне саме для цього рівня).

    Користь = середнє по концептах [(1 - p_known) * I(theta, task)].
    """
    if not task_concepts:
        return 0.0

    irt_params = IRTParams(
        a=task.discrimination,
        b=task.difficulty,
        c=task.guessing,
    )

    contributions = []
    for tc in task_concepts:
        p = knowledge_vector.get(tc.concept_id, 0.5)
        theta = p_known_to_theta(p)
        info = item_information(theta, irt_params)
        contributions.append(tc.weight * (1 - p) * info)

    return sum(contributions) / len(contributions)


def build_pool(
    db: Session,
    user_id: int,
) -> list[KnapsackItem]:
    """
    Формує пул кандидатів для оптимізатора:
    список (task_id, weight=time, value=utility) по всіх активних завданнях.
    """
    # 1) Витягуємо стан знань користувача
    states = db.query(KnowledgeState).filter_by(user_id=user_id).all()
    knowledge_vector = {s.concept_id: s.p_known for s in states}

    # 2) Витягуємо всі активні завдання
    tasks = db.query(Task).filter_by(is_active=True).all()

    pool: list[KnapsackItem] = []
    for task in tasks:
        # витягуємо концепти конкретного завдання
        tcs = db.query(TaskConcept).filter_by(task_id=task.id).all()
        utility = compute_task_utility(task, knowledge_vector, tcs)

        pool.append(
            KnapsackItem(
                task_id=task.id,
                weight=task.estimated_time_seconds,
                value=utility,
            )
        )

    return pool