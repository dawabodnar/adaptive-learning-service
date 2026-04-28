"""
Оптимізаційний модуль — задача про рюкзак для підбору навчальних завдань.

Реалізує 0/1 knapsack методом динамічного програмування.
- weight (вага) — оцінений час виконання завдання, в секундах;
- value (цінність) — навчальна користь завдання для конкретного студента;
- capacity (обмеження) — бюджет часу сесії, в секундах.

Мета: обрати такий набір завдань, що сумарна навчальна користь
максимальна, а сумарний час виконання не перевищує бюджет.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class KnapsackItem:
    task_id: int
    weight: int   # час виконання у секундах
    value: float  # навчальна користь


def solve_knapsack(items: list[KnapsackItem], capacity: int) -> list[int]:
    """
    Розвʼязує 0/1 knapsack методом динамічного програмування.

    Повертає список task_id, що увійшли в оптимальний набір.

    Складність: O(n * capacity) за часом і памʼяттю,
    де n — кількість завдань.
    """
    n = len(items)
    if n == 0 or capacity <= 0:
        return []

    # dp[i][w] = максимальна цінність, використовуючи перші i предметів,
    # маючи бюджет w секунд
    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = items[i - 1]
        for w in range(capacity + 1):
            # варіант 1 — не беремо предмет i
            without_item = dp[i - 1][w]

            # варіант 2 — беремо предмет i (якщо влізає в залишок бюджету)
            if item.weight <= w:
                with_item = dp[i - 1][w - item.weight] + item.value
                dp[i][w] = max(without_item, with_item)
            else:
                dp[i][w] = without_item

    # Зворотний прохід — відновлення набору обраних предметів
    selected: list[int] = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            item = items[i - 1]
            selected.append(item.task_id)
            w -= item.weight

    selected.reverse()
    return selected


def total_weight(items: list[KnapsackItem], selected_ids: list[int]) -> int:
    """Сумарний час виконання обраних завдань."""
    by_id = {item.task_id: item for item in items}
    return sum(by_id[tid].weight for tid in selected_ids if tid in by_id)


def total_value(items: list[KnapsackItem], selected_ids: list[int]) -> float:
    """Сумарна навчальна користь обраних завдань."""
    by_id = {item.task_id: item for item in items}
    return sum(by_id[tid].value for tid in selected_ids if tid in by_id)