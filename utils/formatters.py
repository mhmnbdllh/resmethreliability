"""
utils/formatters.py
===================
Shared numeric formatting utilities used by the reliability engine and
both views. Pure functions, no side effects.
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
