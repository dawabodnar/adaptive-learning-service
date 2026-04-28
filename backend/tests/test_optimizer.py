"""Тести для модуля optimizer.py."""
from app.services.optimizer import KnapsackItem, solve_knapsack, total_value, total_weight


def test_empty_pool_returns_empty():
    selected = solve_knapsack([], capacity=100)
    assert selected == []


def test_single_item_fits():
    items = [KnapsackItem(task_id=1, weight=30, value=5.0)]
    selected = solve_knapsack(items, capacity=60)
    assert selected == [1]


def test_single_item_too_heavy():
    items = [KnapsackItem(task_id=1, weight=120, value=5.0)]
    selected = solve_knapsack(items, capacity=60)
    assert selected == []


def test_picks_higher_value_pair():
    items = [
        KnapsackItem(task_id=1, weight=40, value=5.0),
        KnapsackItem(task_id=2, weight=30, value=4.0),
        KnapsackItem(task_id=3, weight=20, value=3.0),
    ]
    selected = solve_knapsack(items, capacity=60)
    assert total_weight(items, selected) <= 60
    # Оптимально — взяти 2 і 3 (час 50, цінність 7) або 1 і 3 (час 60, цінність 8)
    assert total_value(items, selected) >= 7.0


def test_does_not_exceed_capacity():
    items = [
        KnapsackItem(task_id=1, weight=100, value=10.0),
        KnapsackItem(task_id=2, weight=100, value=10.0),
        KnapsackItem(task_id=3, weight=100, value=10.0),
    ]
    selected = solve_knapsack(items, capacity=150)
    assert total_weight(items, selected) <= 150
    assert len(selected) == 1