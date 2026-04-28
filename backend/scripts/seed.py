"""
Seed-скрипт — наповнює БД тестовими даними:
- 5 концептів (з ієрархією);
- BKT-параметри для кожного концепту;
- 30 навчальних завдань з рандомізованими параметрами IRT.

Запуск:
    python -m scripts.seed
"""
import random

from app.database import SessionLocal
from app.models import BKTParameter, Concept, Task, TaskConcept

random.seed(42)


CONCEPTS = [
    {"name": "Алгебра — основи", "description": "Числа, дії, рівняння"},
    {"name": "Алгебра — функції", "description": "Лінійні та квадратичні функції"},
    {"name": "Геометрія — планіметрія", "description": "Трикутники, чотирикутники, кола"},
    {"name": "Геометрія — стереометрія", "description": "Призми, піраміди, тіла обертання"},
    {"name": "Тригонометрія", "description": "Синуси, косинуси, тотожності"},
]


TASK_TEMPLATES = [
    "Розвʼяжіть рівняння: {expr}",
    "Знайдіть значення виразу: {expr}",
    "Спростіть вираз: {expr}",
    "Обчисліть площу фігури зі стороною {n}",
    "Знайдіть периметр фігури зі стороною {n}",
    "Знайдіть похідну функції y = {expr}",
    "Розкладіть на множники: {expr}",
    "Доведіть, що {expr} = {n}",
]


def seed():
    db = SessionLocal()
    try:
        # 1. Видаляємо все старе у потрібних таблицях
        db.query(TaskConcept).delete()
        db.query(Task).delete()
        db.query(BKTParameter).delete()
        db.query(Concept).delete()
        db.commit()
        print("Старі дані очищено")

        # 2. Створюємо концепти
        concept_objects = []
        for c in CONCEPTS:
            concept = Concept(name=c["name"], description=c["description"])
            db.add(concept)
            concept_objects.append(concept)
        db.flush()
        print(f"Створено {len(concept_objects)} концептів")

        # 3. BKT-параметри для кожного концепту
        for concept in concept_objects:
            params = BKTParameter(
                concept_id=concept.id,
                p_l0=round(random.uniform(0.2, 0.4), 2),
                p_t=round(random.uniform(0.15, 0.25), 2),
                p_g=round(random.uniform(0.15, 0.25), 2),
                p_s=round(random.uniform(0.05, 0.15), 2),
            )
            db.add(params)
        db.flush()
        print(f"Створено BKT-параметри для {len(concept_objects)} концептів")

        # 4. Створюємо 30 завдань
        tasks_created = 0
        for i in range(30):
            template = random.choice(TASK_TEMPLATES)
            expr = f"{random.randint(1, 20)}x + {random.randint(1, 50)}"
            n = random.randint(2, 15)

            content = template.format(expr=expr, n=n)
            answer = str(random.randint(1, 100))

            difficulty = round(random.uniform(-2.0, 2.0), 2)  # b
            discrimination = round(random.uniform(0.5, 2.0), 2)  # a
            guessing = round(random.uniform(0.1, 0.3), 2)  # c
            estimated_time = random.randint(60, 300)  # 1-5 хвилин

            task = Task(
                content=content,
                correct_answer=answer,
                difficulty=difficulty,
                discrimination=discrimination,
                guessing=guessing,
                estimated_time_seconds=estimated_time,
                is_active=True,
            )
            db.add(task)
            db.flush()

            # привʼязуємо до 1-2 рандомних концептів
            num_concepts = random.choice([1, 1, 2])
            chosen = random.sample(concept_objects, num_concepts)
            for concept in chosen:
                tc = TaskConcept(
                    task_id=task.id,
                    concept_id=concept.id,
                    weight=round(random.uniform(0.5, 1.0), 2),
                )
                db.add(tc)

            tasks_created += 1

        db.commit()
        print(f"Створено {tasks_created} завдань")
        print("\nГотово. БД наповнена тестовими даними.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()