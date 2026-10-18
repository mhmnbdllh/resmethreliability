"""
utils/formatters.py
===================
Shared formatting and labelling utilities used across all modules and pages.
All functions are pure (no side effects) and stateless.
"""

import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
# NUMERIC FORMATTERS
# ══════════════════════════════════════════════════════════════════════════════

def _f(v, d=3):
    """
    Format a numeric value to d decimal places.
    Returns '.' for None or NaN (SPSS convention).
    """
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "."
    return f"{v:.{d}f}"


def _p(v, d=3):
    """
    Format a p-value to d decimal places (default 3, matching the
    conventional display precision for most modules).
    Uses standard rounding first (round half up).
    Shows '< .0001'-style threshold (one order below d) only when the
    rounded value is exactly zero at d decimals.
    Shows '.' for None or NaN.
    """
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "."
    try:
        v = float(v)
    except Exception:
        return "."
    rounded = round(v, d)
    if rounded == 0.0:
        thresh = "0" * (d - 1) + "1"
        return f"< .{thresh}"
    return f"{rounded:.{d}f}"


def format_u(v):
    """
    Format Mann-Whitney U statistic to 3 decimal places.
    SPSS always displays U with 3 decimal places (e.g. 6.000, 24.500).
    Returns '.' for None or NaN.
    """
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "."
    return f"{v:.3f}"


# ══════════════════════════════════════════════════════════════════════════════
# EFFECT SIZE LABELS
# ══════════════════════════════════════════════════════════════════════════════

def effect_label_d(d):
    """
    Interpret Cohen's d effect size magnitude.
    Benchmarks: Cohen (1988).
      < .20  → negligible
      .20–.49 → small
      .50–.79 → medium
      ≥ .80  → large
    """
    if d is None or (isinstance(d, float) and np.isnan(d)):
        return "N/A"
    a = abs(d)
    if a < .20: return "negligible"
    if a < .50: return "small"
    if a < .80: return "medium"
    return "large"


def effect_label_r(r):
    """
    Interpret Pearson r / rank-biserial r effect size magnitude.
    Benchmarks: Cohen (1988); Kerby (2014).
      < .10  → negligible
      .10–.29 → small
      .30–.49 → medium
      ≥ .50  → large
    """
    if r is None or (isinstance(r, float) and np.isnan(r)):
        return "N/A"
    a = abs(r)
    if a < .10: return "negligible"
    if a < .30: return "small"
    if a < .50: return "medium"
    return "large"


def effect_label_eta2(eta2):
    """
    Interpret eta-squared (η²) / partial eta-squared effect size magnitude.
    Benchmarks: Cohen (1988).
      < .01  → negligible
      .01–.05 → small
      .06–.13 → medium
      ≥ .14  → large
    """
    if eta2 is None or (isinstance(eta2, float) and np.isnan(eta2)):
        return "N/A"
    a = abs(eta2)
    if a < .01: return "negligible"
    if a < .06: return "small"
    if a < .14: return "medium"
    return "large"


def effect_label_omega2(omega2):
    """
    Interpret omega-squared (ω²) effect size magnitude.
    Benchmarks: Field (2018).
      < .01  → negligible
      .01–.05 → small
      .06–.13 → medium
      ≥ .14  → large
    """
    if omega2 is None or (isinstance(omega2, float) and np.isnan(omega2)):
        return "N/A"
    a = abs(omega2)
    if a < .01: return "negligible"
    if a < .06: return "small"
    if a < .14: return "medium"
    return "large"


# ══════════════════════════════════════════════════════════════════════════════
# POWER LABELS
# ══════════════════════════════════════════════════════════════════════════════

def power_label(power):
    """
    Classify achieved statistical power.
    Benchmark: Cohen (1988) — minimum recommended power = .80.
      ≥ .95  → Excellent
      ≥ .80  → Adequate
      ≥ .60  → Moderate
      < .60  → Low
    """
    if power is None or (isinstance(power, float) and np.isnan(power)):
        return "N/A"
    if power >= .95: return "Excellent (\u2265\u2009.95)"
    if power >= .80: return "Adequate (\u2265\u2009.80)"
    if power >= .60: return "Moderate (.60\u2013.79)"
    return "Low (< .60) \u2014 consider increasing sample size"


# ══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════════

REFERENCES = {
    "cohen_1988":
        "Cohen, J. (1988). Statistical power analysis for the behavioral "
        "sciences (2nd ed.). Lawrence Erlbaum Associates.",
    "field_2018":
        "Field, A. (2018). Discovering statistics using IBM SPSS statistics "
        "(5th ed.). SAGE Publications.",
    "razali_wah_2011":
        "Razali, N. M., & Wah, Y. B. (2011). Power comparisons of "
        "Shapiro-Wilk, Kolmogorov-Smirnov, Lilliefors and Anderson-Darling "
        "tests. Journal of Statistical Modeling and Analytics, 2(1), 21\u201333.",
    "lilliefors_1967":
        "Lilliefors, H. W. (1967). On the Kolmogorov-Smirnov test for "
        "normality with mean and variance unknown. Journal of the American "
        "Statistical Association, 62(318), 399\u2013402.",
    "shapiro_wilk_1965":
        "Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test "
        "for normality (complete samples). Biometrika, 52(3\u20134), 591\u2013611.",
    "kerby_2014":
        "Kerby, D. S. (2014). The simple difference formula: An approach to "
        "teaching nonparametric correlation. Comprehensive Psychology, 3, "
        "11.IT.3.1.",
    "efron_tibshirani_1993":
        "Efron, B., & Tibshirani, R. J. (1993). An introduction to the "
        "bootstrap. Chapman & Hall.",
}
