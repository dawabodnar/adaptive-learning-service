"""
Профілювання алгоритмів BKT, IRT, Knapsack
cProfile + Pyinstrument для БКР
"""
import cProfile
import pstats
import io
import time
import random

# ── імпорт алгоритмів (копії з твого коду) ──────────────────────────────────
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class BKTParams:
    p_l0: float = 0.3; p_t: float = 0.2; p_g: float = 0.2; p_s: float = 0.1

def update_knowledge(p_known_prev, is_correct, params):
    p = p_known_prev
    if is_correct:
        num = p * (1 - params.p_s); den = p * (1 - params.p_s) + (1 - p) * params.p_g
    else:
        num = p * params.p_s; den = p * params.p_s + (1 - p) * (1 - params.p_g)
    p_post = num / den if den > 0 else p
    return p_post + (1 - p_post) * params.p_t

@dataclass(frozen=True)
class IRTParams:
    a: float = 1.0; b: float = 0.0; c: float = 0.25

def probability_correct(theta, params):
    return params.c + (1 - params.c) / (1 + math.exp(params.a * (params.b - theta)))

def item_information(theta, params):
    p = probability_correct(theta, params)
    if p <= params.c or p >= 1.0: return 0.0
    num = params.a**2 * (p - params.c)**2 * (1 - p)
    den = (1 - params.c)**2 * p
    return num / den if den > 0 else 0.0

@dataclass(frozen=True)
class KnapsackItem:
    task_id: int; weight: int; value: float

def solve_knapsack(items, capacity):
    n = len(items)
    if n == 0 or capacity <= 0: return []
    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        item = items[i - 1]
        for w in range(capacity + 1):
            without = dp[i - 1][w]
            if item.weight <= w:
                dp[i][w] = max(without, dp[i - 1][w - item.weight] + item.value)
            else:
                dp[i][w] = without
    selected, w = [], capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(items[i - 1].task_id); w -= items[i - 1].weight
    selected.reverse(); return selected

# ── робочі навантаження ──────────────────────────────────────────────────────
def workload_bkt(n=20):
    params = BKTParams(); p = 0.3
    for i in range(n):
        p = update_knowledge(p, i % 2 == 0, params)

def workload_irt(n=100):
    params = IRTParams()
    for theta in [i * 0.06 - 3 for i in range(n)]:
        probability_correct(theta, params)
        item_information(theta, params)

def workload_knapsack():
    random.seed(42)
    items = [KnapsackItem(i, random.randint(60, 300), random.uniform(0.1, 1.0))
             for i in range(60)]
    solve_knapsack(items, 1800)

def full_recommend_cycle():
    """Симуляція одного /recommend запиту."""
    workload_bkt(); workload_irt(); workload_knapsack()

# ── cProfile ─────────────────────────────────────────────────────────────────
def run_cprofile():
    pr = cProfile.Profile()
    pr.enable()
    for _ in range(50):
        full_recommend_cycle()
    pr.disable()

    buf = io.StringIO()
    ps = pstats.Stats(pr, stream=buf).sort_stats("cumulative")
    ps.print_stats(20)
    return buf.getvalue()

# ── ручний таймер (як Pyinstrument-замінник без залежностей) ─────────────────
def run_manual_timer():
    results = {}
    for name, fn, reps in [
        ("BKT  update_knowledge ×20",    workload_bkt,      500),
        ("IRT  item_information ×100",   workload_irt,      500),
        ("Knapsack 60 items / 1800s",    workload_knapsack,  50),
        ("Full /recommend cycle",         full_recommend_cycle, 50),
    ]:
        t0 = time.perf_counter()
        for _ in range(reps): fn()
        elapsed_ms = (time.perf_counter() - t0) / reps * 1000
        results[name] = elapsed_ms
    return results

# ── головний блок ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SEP = "=" * 64

    print(f"\n{SEP}")
    print("  ПРОФІЛЮВАННЯ АЛГОРИТМІВ  |  cProfile")
    print(f"{SEP}\n")
    print(run_cprofile())

    print(f"\n{SEP}")
    print("  ЛАТЕНТНІСТЬ НА ВИКЛИК  |  ручний таймер (≈ Pyinstrument)")
    print(f"{SEP}\n")
    timings = run_manual_timer()
    col = max(len(k) for k in timings) + 2
    for name, ms in timings.items():
        bar = "█" * max(1, int(ms * 3))
        print(f"  {name:<{col}} {ms:>8.4f} мс  {bar}")

    print(f"\n{SEP}")
    print("  ПІДСУМОК ДЛЯ БКР")
    print(f"{SEP}")
    rec = timings.get("Full /recommend cycle", 0)
    print(f"\n  Один /recommend запит (Pure Python): {rec:.3f} мс")
    print(f"  Вузьке місце: Knapsack ({timings.get('Knapsack 60 items / 1800s', 0):.3f} мс)")
    print(f"  BKT:          {timings.get('BKT  update_knowledge ×20', 0):.4f} мс")
    print(f"  IRT:          {timings.get('IRT  item_information ×100', 0):.4f} мс")
    print()