# benchmark_models.py  — зберегти у backend/
"""
Запуск:
  cd backend
  venv\\Scripts\\activate        (Windows)
  source venv/bin/activate     (Mac/Linux)
  pip install numba tabulate
  python benchmark_models.py
"""

import sys, time
import numpy as np
from numba import njit
from tabulate import tabulate

sys.path.insert(0, ".")  # щоб знайшов пакет app

from app.services.bkt import BKTParams, update_knowledge
from app.services.irt import IRTParams, probability_correct, item_information
from app.services.optimizer import KnapsackItem, solve_knapsack

# ─── NUMBA-версії (точні копії вашої логіки) ──────────────────────────────────

@njit(cache=True, fastmath=True)
def _bkt_numba(p_known, is_correct, p_l0, p_t, p_g, p_s):
    p = p_known
    if is_correct:
        num = p * (1.0 - p_s)
        den = num + (1.0 - p) * p_g
    else:
        num = p * p_s
        den = num + (1.0 - p) * (1.0 - p_g)
    p_post = num / den if den > 0.0 else p
    return p_post + (1.0 - p_post) * p_t


@njit(cache=True, fastmath=True)
def _bkt_session_numba(p_l0, p_t, p_g, p_s, responses):
    """responses: масив 1.0/0.0"""
    p = p_l0
    for i in range(len(responses)):
        correct = responses[i] == 1.0
        if correct:
            num = p * (1.0 - p_s)
            den = num + (1.0 - p) * p_g
        else:
            num = p * p_s
            den = num + (1.0 - p) * (1.0 - p_g)
        p_post = num / den if den > 0.0 else p
        p = p_post + (1.0 - p_post) * p_t
    return p


@njit(cache=True, fastmath=True)
def _irt_batch_numba(theta, a_arr, b_arr, c_arr):
    """Повертає item_information для всіх завдань одразу."""
    n = len(a_arr)
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        z = -a_arr[i] * (theta - b_arr[i])
        p = c_arr[i] + (1.0 - c_arr[i]) / (1.0 + np.exp(z))
        c = c_arr[i]
        if p <= c or p >= 1.0:
            out[i] = 0.0
        else:
            num = a_arr[i] ** 2 * (p - c) ** 2 * (1.0 - p)
            den = (1.0 - c) ** 2 * p
            out[i] = num / den if den > 0.0 else 0.0
    return out


@njit(cache=True)
def _knapsack_numba(weights, values, capacity):
    n = len(weights)
    dp = np.zeros((n + 1, capacity + 1), dtype=np.float64)
    for i in range(1, n + 1):
        wi = weights[i - 1]
        vi = values[i - 1]
        for w in range(capacity + 1):
            dp[i, w] = dp[i - 1, w]
            if wi <= w:
                alt = dp[i - 1, w - wi] + vi
                if alt > dp[i, w]:
                    dp[i, w] = alt
    return dp[n, capacity]


# ─── JIT прогрів ──────────────────────────────────────────────────────────────

def warmup():
    print("⏳ Numba JIT компіляція...", end=" ", flush=True)
    t = time.perf_counter()
    _bkt_session_numba(0.3, 0.2, 0.2, 0.1, np.array([1.0, 0.0]))
    _irt_batch_numba(0.0,
                     np.array([1.0]), np.array([0.0]), np.array([0.25]))
    _knapsack_numba(np.array([60], dtype=np.int32),
                    np.array([1.0]), 120)
    print(f"готово ({(time.perf_counter()-t)*1000:.0f} ms)\n")


# ─── Benchmark helper ─────────────────────────────────────────────────────────

def bench(fn, n=500):
    fn()  # прогрів CPU branch predictor
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - t0) / n * 1000  # ms


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    warmup()
    np.random.seed(42)

    # ── BKT: сесія з 20 відповідей ────────────────────────────────────────────
    raw = np.random.randint(0, 2, 20).tolist()
    responses_bool = [bool(r) for r in raw]
    responses_np   = np.array(raw, dtype=np.float64)
    params = BKTParams(p_l0=0.3, p_t=0.2, p_g=0.2, p_s=0.1)

    def bkt_pure_session():
        p = params.p_l0
        for r in responses_bool:
            p = update_knowledge(p, r, params)
        return p

    def bkt_nb_session():
        return _bkt_session_numba(
            params.p_l0, params.p_t, params.p_g, params.p_s, responses_np)

    t_bkt_py = bench(bkt_pure_session)
    t_bkt_nb = bench(bkt_nb_session)

    # ── IRT: 100 завдань, обчислення item_information ─────────────────────────
    N = 100
    a = np.random.uniform(0.5, 2.0, N)
    b = np.random.normal(0.0, 1.0, N)
    c = np.random.uniform(0.1, 0.3, N)
    irt_params_list = [IRTParams(a=a[i], b=b[i], c=c[i]) for i in range(N)]
    theta = 0.5

    def irt_pure_batch():
        return [item_information(theta, p) for p in irt_params_list]

    def irt_nb_batch():
        return _irt_batch_numba(theta, a, b, c)

    t_irt_py = bench(irt_pure_batch)
    t_irt_nb = bench(irt_nb_batch)

    # ── Knapsack: 60 завдань, бюджет 1800 с ───────────────────────────────────
    K = 60
    capacity = 1800
    weights_list = np.random.randint(60, 600, K).tolist()
    values_list  = np.random.uniform(0.5, 5.0, K).tolist()
    items = [KnapsackItem(task_id=i,
                          weight=weights_list[i],
                          value=values_list[i]) for i in range(K)]
    weights_np = np.array(weights_list, dtype=np.int32)
    values_np  = np.array(values_list,  dtype=np.float64)

    def ks_pure():
        return solve_knapsack(items, capacity)

    def ks_nb():
        return _knapsack_numba(weights_np, values_np, capacity)

    t_ks_py = bench(ks_pure,  n=100)
    t_ks_nb = bench(ks_nb,    n=100)

    # ── Таблиця ───────────────────────────────────────────────────────────────
    def speedup(a, b):
        return f"×{a/b:.0f}" if b > 0 else "—"

    rows = [
        ["BKT — update_knowledge × 20",
         f"{t_bkt_py:.4f}", f"{t_bkt_nb:.5f}", speedup(t_bkt_py, t_bkt_nb)],
        [f"IRT 3PL — item_information × {N}",
         f"{t_irt_py:.4f}", f"{t_irt_nb:.5f}", speedup(t_irt_py, t_irt_nb)],
        [f"Knapsack 0/1 — {K} завдань / {capacity} с",
         f"{t_ks_py:.3f}",  f"{t_ks_nb:.4f}",  speedup(t_ks_py,  t_ks_nb)],
    ]

    print(tabulate(rows,
        headers=["Алгоритм", "Ваш код (мс)", "Numba/LLVM (мс)", "Прискорення"],
        tablefmt="rounded_outline",
        colalign=("left", "right", "right", "right")))

    total_py = t_bkt_py + t_irt_py + t_ks_py
    total_nb = t_bkt_nb + t_irt_nb + t_ks_nb
    print(f"\n  Загальний час на один /recommend запит:")
    print(f"    Ваш код (Pure Python) : {total_py:.3f} мс")
    print(f"    Numba / LLVM          : {total_nb:.4f} мс")
    print(f"    Виграш                : −{total_py - total_nb:.3f} мс\n")


if __name__ == "__main__":
    main()