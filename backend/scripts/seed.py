"""
Seed-скрипт — наповнює БД реальними завданнями з варіантами відповідей.
"""
import random

from app.database import SessionLocal
from app.models import (
    BKTParameter, Concept, KnowledgeState,
    LearningSession, SessionTask, Task, TaskConcept,
)


CONCEPTS = [
    {"name": "Англійська — граматика",
     "description": "Базові правила: артиклі, часи, прийменники"},
    {"name": "Англійська — лексика",
     "description": "Базовий словниковий запас, переклад"},
    {"name": "Програмування — основи Python",
     "description": "Синтаксис, типи даних, базові оператори"},
    {"name": "Математика — арифметика",
     "description": "Додавання, віднімання, множення, ділення, відсотки"},
    {"name": "Математика — алгебра",
     "description": "Лінійні рівняння, ступені, прості перетворення"},
]


# (content, correct_answer, options or None, concept_idx, answer_type, est_time, difficulty)
TASKS = [
    # ── 1. Англійська — граматика (з варіантами) ────────────────────────
    ("She ___ to school every day.", "goes",
     ["go", "goes", "going"], 0, "text", 45, -1.0),
    ("I see ___ cat in the garden.", "a",
     ["a", "an", "the"], 0, "text", 30, -1.5),
    ("There ___ many books on the table.", "are",
     ["is", "are"], 0, "text", 30, -1.2),
    ("Yesterday I ___ a movie.", "watched",
     ["watch", "watched", "watching"], 0, "text", 45, -0.5),
    ("This is ___ book.", "my",
     ["my", "me", "I"], 0, "text", 30, -1.5),
    ("The cat is ___ the table.", "on",
     ["on", "in", "at"], 0, "text", 45, -0.8),

    # ── 2. Англійська — лексика (частково з варіантами) ─────────────────
    ("Перекладіть на англійську: «книга»", "book",
     None, 1, "text", 30, -2.0),
    ("Перекладіть на англійську: «вчитель»", "teacher",
     None, 1, "text", 45, -1.5),
    ("Що означає слово 'apple' українською?", "яблуко",
     ["яблуко", "груша", "стіл", "сонце"], 1, "text", 30, -2.0),
    ("Перекладіть на англійську: «червоний»", "red",
     None, 1, "text", 30, -1.8),
    ("Що є антонімом слова 'big'?", "small",
     ["small", "tall", "fast", "blue"], 1, "text", 45, -0.5),
    ("Перекладіть на англійську: «вода»", "water",
     None, 1, "text", 30, -2.0),

    # ── 3. Програмування — Python (частково з варіантами) ───────────────
    ("Який результат виразу: 5 + 3 * 2 ?", "11",
     None, 2, "number", 60, -0.5),
    ("Що виведе print(10 // 3) у Python?", "3",
     None, 2, "number", 60, 0.5),
    ("Який тип даних поверне type(3.14) ?", "float",
     ["int", "float", "str", "bool"], 2, "text", 45, 0.0),
    ("Скільки елементів у списку [1, 2, 3, 4, 5] ?", "5",
     None, 2, "number", 30, -1.5),
    ("Що виведе print(len('Hello')) ?", "5",
     None, 2, "number", 45, -0.3),
    ("Який оператор перевіряє рівність у Python?", "==",
     ["=", "==", "===", "!="], 2, "text", 30, 0.0),

    # ── 4. Математика — арифметика (без варіантів) ──────────────────────
    ("Обчисліть: 15 + 27", "42", None, 3, "number", 30, -2.0),
    ("Обчисліть: 84 - 36", "48", None, 3, "number", 45, -1.5),
    ("Обчисліть: 9 × 7", "63", None, 3, "number", 30, -1.5),
    ("Обчисліть: 144 ÷ 12", "12", None, 3, "number", 45, -1.0),
    ("Обчисліть: 2 у кубі (2³)", "8", None, 3, "number", 30, -1.5),
    ("Скільки буде 50% від 200?", "100", None, 3, "number", 45, -1.0),

    # ── 5. Математика — алгебра (без варіантів) ─────────────────────────
    ("Розвʼяжіть: x + 5 = 12. Знайдіть x.", "7", None, 4, "number", 60, -1.0),
    ("Розвʼяжіть: 2x = 18. Знайдіть x.", "9", None, 4, "number", 60, -0.8),
    ("Розвʼяжіть: x - 7 = 3. Знайдіть x.", "10", None, 4, "number", 60, -1.0),
    ("Знайдіть x з рівняння: 3x + 1 = 10", "3", None, 4, "number", 75, 0.0),
    ("Чому дорівнює x² при x = 4 ?", "16", None, 4, "number", 30, -1.5),
    ("Розвʼяжіть: x ÷ 2 = 6. Знайдіть x.", "12", None, 4, "number", 45, -1.0),
]


def seed():
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)  # створює таблиці, якщо їх ще нема
    
    random.seed(42)
    db = SessionLocal()
    try:
        db.query(SessionTask).delete()
        db.query(LearningSession).delete()
        db.query(KnowledgeState).delete()
        db.query(TaskConcept).delete()
        db.query(BKTParameter).delete()
        db.query(Task).delete()
        db.query(Concept).delete()
        db.commit()
        print("Старі дані очищено")

        concept_objects = []
        for c in CONCEPTS:
            concept = Concept(name=c["name"], description=c["description"])
            db.add(concept)
            concept_objects.append(concept)
        db.flush()
        print(f"Створено {len(concept_objects)} концептів")

        for concept in concept_objects:
            params = BKTParameter(
                concept_id=concept.id,
                p_l0=round(random.uniform(0.25, 0.40), 2),
                p_t=round(random.uniform(0.18, 0.25), 2),
                p_g=round(random.uniform(0.15, 0.22), 2),
                p_s=round(random.uniform(0.05, 0.12), 2),
            )
            db.add(params)
        db.flush()
        print(f"Створено BKT-параметри для {len(concept_objects)} концептів")

        tasks_created = 0
        for content, answer, options, concept_idx, ans_type, est_time, difficulty in TASKS:
            task = Task(
                content=content,
                correct_answer=answer,
                options=options,
                difficulty=difficulty,
                discrimination=round(random.uniform(0.8, 1.6), 2),
                guessing=round(random.uniform(0.15, 0.25), 2),
                estimated_time_seconds=est_time,
                answer_type=ans_type,
                is_active=True,
            )
            db.add(task)
            db.flush()

            tc = TaskConcept(
                task_id=task.id,
                concept_id=concept_objects[concept_idx].id,
                weight=1.0,
            )
            db.add(tc)

            tasks_created += 1

        db.commit()
        print(f"Створено {tasks_created} завдань")
        print(f"  - з варіантами відповіді: "
              f"{sum(1 for t in TASKS if t[2] is not None)}")
        print(f"  - з вписуванням:          "
              f"{sum(1 for t in TASKS if t[2] is None)}")
        print("\nГотово.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()