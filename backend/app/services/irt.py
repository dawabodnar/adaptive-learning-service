"""
Теорія відповіді на завдання (Item Response Theory).

Реалізує тримараметричну логістичну модель (3PL) — формула 1.4 з Розділу 1.

Параметри завдання:
- a: дискримінація (наскільки добре завдання розрізняє учнів різних рівнів)
- b: складність (рівень знань, на якому ймовірність правильної відповіді = (1+c)/2)
- c: ймовірність вгадування (нижня асимптота)
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class IRTParams:
    a: float = 1.0
    b: float = 0.0
    c: float = 0.25


def probability_correct(theta: float, params: IRTParams) -> float:
    """
    Ймовірність правильної відповіді студента з рівнем знань theta.

    Формула 1.4:
        P(X=1 | theta) = c + (1 - c) / (1 + exp(-a * (theta - b)))
    """
    z = -params.a * (theta - params.b)
    return params.c + (1 - params.c) / (1 + math.exp(z))


def item_information(theta: float, params: IRTParams) -> float:
    """
    Інформаційна функція завдання I(theta).

    Чим вище значення — тим краще завдання розрізняє рівень студента
    в околі theta. Використовується для адаптивного підбору завдань.

    Для 3PL-моделі:
        I(theta) = a^2 * (P - c)^2 * (1 - P) / ((1 - c)^2 * P)

    де P = P(X=1 | theta).
    """
    p = probability_correct(theta, params)
    if p <= params.c or p >= 1.0:
        return 0.0
    numerator = params.a ** 2 * (p - params.c) ** 2 * (1 - p)
    denominator = (1 - params.c) ** 2 * p
    return numerator / denominator if denominator > 0 else 0.0