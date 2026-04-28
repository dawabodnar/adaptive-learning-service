"""
Байєсівське відстеження знань (Bayesian Knowledge Tracing).

Реалізує формули 1.1, 1.2, 1.3 з Розділу 1 БКР.

Параметри моделі:
- p_l0: початкова ймовірність знання концепту до навчання
- p_t:  ймовірність засвоєння концепту після однієї взаємодії
- p_g:  ймовірність правильної відповіді за відсутності знання (вгадування)
- p_s:  ймовірність хибної відповіді попри наявність знання (помилка)
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BKTParams:
    p_l0: float = 0.3
    p_t: float = 0.2
    p_g: float = 0.2
    p_s: float = 0.1


def update_knowledge(
    p_known_prev: float,
    is_correct: bool,
    params: BKTParams,
) -> float:
    """
    Оновлює ймовірність знання концепту після відповіді студента.

    Формула 1.1 (правильна відповідь):
        P(L_n | correct) = P(L_n-1)*(1-P(S)) /
                           [P(L_n-1)*(1-P(S)) + (1-P(L_n-1))*P(G)]

    Формула 1.2 (хибна відповідь):
        P(L_n | incorrect) = P(L_n-1)*P(S) /
                             [P(L_n-1)*P(S) + (1-P(L_n-1))*(1-P(G))]

    Формула 1.3 (ефект навчання):
        P(L_n) = P(L_n | resp) + (1 - P(L_n | resp)) * P(T)
    """
    p = p_known_prev

    # Формули 1.1 / 1.2 — апостеріорна ймовірність знання
    if is_correct:
        numerator = p * (1 - params.p_s)
        denominator = p * (1 - params.p_s) + (1 - p) * params.p_g
    else:
        numerator = p * params.p_s
        denominator = p * params.p_s + (1 - p) * (1 - params.p_g)

    p_posterior = numerator / denominator if denominator > 0 else p

    # Формула 1.3 — врахування ефекту навчання
    p_new = p_posterior + (1 - p_posterior) * params.p_t

    return p_new