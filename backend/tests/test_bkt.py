"""Тести для модуля BKT — services/bkt.py."""
import pytest

from app.services.bkt import BKTParams, update_knowledge


def test_correct_answer_increases_p_known():
    params = BKTParams(p_l0=0.3, p_t=0.2, p_g=0.2, p_s=0.1)
    p_new = update_knowledge(p_known_prev=0.3, is_correct=True, params=params)
    assert p_new > 0.3


def test_incorrect_answer_decreases_p_known_before_learning():
    """Хибна відповідь зменшує апостеріорну ймовірність,
    але ефект навчання потім трохи компенсує."""
    params = BKTParams(p_l0=0.3, p_t=0.0, p_g=0.2, p_s=0.1)  # p_t=0 — без навчання
    p_new = update_knowledge(p_known_prev=0.5, is_correct=False, params=params)
    assert p_new < 0.5


def test_p_known_stays_in_unit_interval():
    params = BKTParams()
    for prev in [0.01, 0.5, 0.99]:
        for is_correct in [True, False]:
            p_new = update_knowledge(prev, is_correct, params)
            assert 0.0 <= p_new <= 1.0


def test_high_p_known_with_correct_answer_approaches_one():
    params = BKTParams(p_l0=0.95, p_t=0.2, p_g=0.2, p_s=0.1)
    p_new = update_knowledge(p_known_prev=0.95, is_correct=True, params=params)
    assert p_new > 0.95