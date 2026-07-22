"""抽牌概率计算模块。

牌库共 N 张牌，其中 K 张为关键牌。所有计算使用 Fraction 保留精确分数，
前端展示时再转换为浮点数百分比。
"""

from fractions import Fraction
from itertools import groupby
from math import comb
from typing import Dict, List


def hypergeom_pmf(N: int, K: int, n: int, k: int) -> Fraction:
    """无放回超几何分布：P(X = k)。

    公式：P(X = k) = C(K, k) * C(N - K, n - k) / C(N, n)
    当 k 超出可行范围时返回 0。
    """
    if not (0 <= k <= K and 0 <= n - k <= N - K):
        return Fraction(0, 1)
    return Fraction(comb(K, k) * comb(N - K, n - k), comb(N, n))


def hypergeom_at_least(N: int, K: int, n: int, t: int) -> Fraction:
    """无放回超几何分布：P(X >= t)。

    对 k = t .. min(n, K) 求和 pmf(k)。t <= 0 时概率为 1。
    """
    if t <= 0:
        return Fraction(1, 1)
    upper = min(n, K)
    return sum((hypergeom_pmf(N, K, n, k) for k in range(t, upper + 1)), Fraction(0, 1))


def hypergeom_expected_value(N: int, K: int, n: int) -> Fraction:
    """超几何分布期望：E[X] = n * K / N。"""
    return Fraction(n * K, N)


def problem1_score_distribution(N: int, K: int, a: int, b: int) -> Dict:
    """问题 1：一次性抽 a 张牌，计算得分 0、至少 1、...、至少 b 的概率。

    返回字段：
    - N, K, a, b：输入参数
    - pmf：[(k, exact, pct), ...], k = 0..a
    - at_least：[(k, exact, pct), ...], k = 0..min(b,a)
    - expected_value：浮点期望值
    """
    pmf = []
    for k in range(0, a + 1):
        p = hypergeom_pmf(N, K, a, k)
        pmf.append(_point(k, p))

    upper_b = min(b, a)
    at_least = []
    for t in range(0, upper_b + 1):
        p = hypergeom_at_least(N, K, a, t)
        at_least.append(_point(t, p))

    return {
        'N': N,
        'K': K,
        'a': a,
        'b': b,
        'pmf': pmf,
        'at_least': at_least,
        'expected_value': float(hypergeom_expected_value(N, K, a)),
    }


def problem2_group_probabilities(groups: List[Dict]) -> List[Dict]:
    """问题 2：每种花色点数组合中抽到关键牌的概率。

    groups 元素结构：{'suit': str, 'rank': int, 'size': int, 'keys': int, ...}
    返回每个 group 附带 'prob'（浮点）、'prob_exact'（分数字符串）和 'prob_pct'（百分比）。
    """
    result = []
    for g in groups:
        size = g['size']
        keys = g['keys']
        prob = Fraction(keys, size) if size > 0 else Fraction(0, 1)
        entry = dict(g)
        entry['prob'] = float(prob)
        entry['prob_exact'] = str(prob)
        entry['prob_pct'] = _pct(prob)
        result.append(entry)
    return result


def problem3_probabilities(N: int, K: int, groups: List[Dict], a: int) -> Dict:
    """问题 3：新手 vs 高手策略概率。

    - 新手：随机从抽出的 a 张牌中选择一张，成功概率 = K / N。
    - 高手：选择抽出牌中关键概率 q_i 最大的一张。
      利用累计组合数计算：
      P_expert = sum_j q_j * [C(C_j, a) - C(C_{j-1}, a)] / C(N, a)
      其中 C_j 为关键概率 <= q_j 的累计牌数。
    """
    newbie = Fraction(K, N)

    if a == 0:
        expert = Fraction(0, 1)
    else:
        # 按 q_i 升序排列，并将相同概率的组合合并累计张数
        group_probs = sorted(
            (Fraction(g['keys'], g['size']) if g['size'] > 0 else Fraction(0, 1), g['size'])
            for g in groups
        )

        unique_q = []
        for q, items in groupby(group_probs, key=lambda x: x[0]):
            total_size = sum(size for _, size in items)
            unique_q.append((q, total_size))

        # 计算累计牌数 C_j
        cumulative = 0
        cumulative_counts = []
        for q, size in unique_q:
            cumulative += size
            cumulative_counts.append((q, cumulative))

        denom = comb(N, a)
        expert = Fraction(0, 1)
        prev_count = 0
        for q, count in cumulative_counts:
            if count >= a:
                term = Fraction(comb(count, a) - (comb(prev_count, a) if prev_count >= a else 0), denom)
            else:
                term = Fraction(0, 1)
            expert += q * term
            prev_count = count

    return {
        'N': N,
        'K': K,
        'a': a,
        'newbie': _strategy_point(newbie),
        'expert': _strategy_point(expert),
    }


def _point(k: int, prob: Fraction) -> Dict:
    """构建问题 1 单点概率返回结构。"""
    return {
        'k': k,
        'exact': str(prob),
        'pct': _pct(prob),
    }


def _strategy_point(prob: Fraction) -> Dict:
    """构建问题 3 策略概率返回结构。"""
    return {
        'exact': str(prob),
        'pct': _pct(prob),
    }


def _pct(prob: Fraction) -> float:
    """将精确分数转换为保留 4 位小数的百分比浮点数。"""
    return round(float(prob) * 100, 4)
