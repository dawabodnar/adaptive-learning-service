"""Тести для модуля IRT — services/irt.py."""
import math

from app.services.irt import IRTParams, item_information, probability_correct


def test_probability_at_difficulty_equals_midpoint():
    """При theta = b ймовірність правильної відповіді = c + (1-c)/2."""
    params = IRTParams(a=1.0, b=0.0, c=0.25)
    p = probability_correct(theta=0.0, params=params)
    assert math.isclose(p, 0.25 + 0.75 / 2, abs_tol=1e-9)


def test_probability_high_theta_close_to_one():
    params = IRTParams(a=1.0, b=0.0, c=0.25)
    p = probability_correct(theta=10.0, params=params)
    assert p > 0.99


def test_probability_low_theta_close_to_guessing():
    params = IRTParams(a=1.0, b=0.0, c=0.25)
    p = probability_correct(theta=-10.0, params=params)
    assert math.isclose(p, 0.25, abs_tol=0.01)


def test_information_max_near_difficulty():
    """Інформаційна функція максимальна біля theta = b."""
    params = IRTParams(a=1.0, b=0.5, c=0.25)
    i_at_b = item_information(theta=0.5, params=params)
    i_far = item_information(theta=3.0, params=params)
    assert i_at_b > i_far


def test_information_non_negative():
    params = IRTParams(a=1.5, b=0.0, c=0.2)
    for theta in [-3.0, -1.0, 0.0, 1.0, 3.0]:
        info = item_information(theta=theta, params=params)
        assert info >= 0.0