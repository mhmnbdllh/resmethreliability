"""
tests/test_irar_formulas.py
============================
Permanent, re-runnable correctness check for every Inter-Rater Agreement
(ResMeth-IRA) coefficient in modules/reliability.py.

WHY THIS FILE EXISTS
---------------------
Every verification claim in reliability.py's own docstrings (independent
cross-validation against scikit-learn, pingouin, the `krippendorff`
package, hand-reconstructed primary-source formulas, Monte Carlo checks,
etc.) was real work that was actually done -- but it was done through
throwaway scripts that were never committed to this repository. That means
none of it could be re-run automatically to catch a future regression; it
only existed as prose. This file fixes that: it is committed, and it is
meant to be re-run every time reliability.py or the sample CSVs change.

WHAT THIS FILE CHECKS, AND HOW EACH CHECK IS INDEPENDENT OF THE ENGINE
-----------------------------------------------------------------------
Three different kinds of check are used, because they catch different
kinds of error:

  1. INDEPENDENT-LIBRARY checks (Krippendorff's alpha vs. the `krippendorff`
     PyPI package; Cohen's kappa vs. scikit-learn directly; ICC vs. pingouin
     directly). These do not import or call anything from this module's own
     helper functions -- a bug in reliability.py's own code cannot make
     these pass by accident.

  2. HAND-DERIVED checks (Scott's pi, Brennan-Prediger, Gwet's AC1, Fleiss'
     kappa, Lin's CCC). Each coefficient is recomputed in THIS file, from
     the raw rating columns, using only numpy -- written independently of
     reliability.py's own internal functions (_scott_pi, _brennan_prediger,
     etc. are never called here). This also does not need the formula
     itself to be trusted twice: it IS the formula, written out a second
     time by hand, from the primary-source definition in Method details of
     the accompanying MethodsX manuscript.

  3. STRUCTURAL-IDENTITY checks (Gwet's AC2 with identity weights must equal
     Gwet's AC1 exactly -- a mathematical requirement, not a coincidence).

  4. REGRESSION checks against the exact values already published in the
     manuscript's Method validation "End-to-end verification" tables
     (S1-S6). These do NOT prove correctness on their own (they ultimately
     trace back to this same engine), but they catch any future
     unintentional change to the numbers -- which is the specific gap this
     file was written to close.

HOW TO RUN
----------
    python3 tests/test_irar_formulas.py

No pytest dependency is required -- this is a plain script so it can be
run on a fresh clone with nothing beyond requirements.txt, EXCEPT for one
test-only dependency not needed by the deployed app itself:

    pip install krippendorff

If that package is not installed, the independent-library check for
Krippendorff's alpha is skipped (clearly reported as SKIPPED, not silently
passed) -- every other check still runs.

Exit code is 0 if every check passed, 1 if anything failed or errored.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd

from modules.reliability import run_multi_irar

try:
    import krippendorff as _kd_pkg
    _HAVE_KD_PKG = True
except ImportError:
    _HAVE_KD_PKG = False

try:
    from sklearn.metrics import cohen_kappa_score as _sklearn_kappa
    _HAVE_SKLEARN = True
except ImportError:
    _HAVE_SKLEARN = False

try:
    import pingouin as _pg
    _HAVE_PINGOUIN = True
except ImportError:
    _HAVE_PINGOUIN = False


# ══════════════════════════════════════════════════════════════════════════
# Result collection
# ══════════════════════════════════════════════════════════════════════════

_RESULTS = []  # list of (name, status, detail) ; status in PASS/FAIL/SKIP/ERROR


def _record(name, ok, detail, skipped=False):
    status = "SKIP" if skipped else ("PASS" if ok else "FAIL")
    _RESULTS.append((name, status, detail))


def _check(name, a, b, tol=1e-6):
    try:
        diff = abs(float(a) - float(b))
        _record(name, diff <= tol, f"a={a!r} b={b!r} diff={diff:.3e} tol={tol:.1e}")
    except Exception as e:
        _RESULTS.append((name, "ERROR", f"{type(e).__name__}: {e}"))


def _skip(name, reason):
    _record(name, True, reason, skipped=True)


# ══════════════════════════════════════════════════════════════════════════
# Load the 3 real sample datasets shipped with the repo
# ══════════════════════════════════════════════════════════════════════════

_DF_DICH = pd.read_csv(_ROOT / "sample-resmeth_Dichotomous.csv")
_DF_ORD  = pd.read_csv(_ROOT / "sample-resmeth_Nominal-Ordinal.csv")
_DF_IR   = pd.read_csv(_ROOT / "sample-resmeth_Interval-Ratio.csv")

# The 6 data-type x rater-count configurations documented in the manuscript's
# Method validation, "End-to-end verification across all six data-type x
# rater-count configurations" section.
_SCENARIOS = {
    "S1_dichotomous_k2": (_DF_DICH, [{"name": "S1", "items": ["R1", "R2"],
                                       "data_type": "dichotomous", "q_declared": 2}]),
    "S2_dichotomous_k4": (_DF_DICH, [{"name": "S2", "items": ["R1", "R2", "R3", "R4"],
                                       "data_type": "dichotomous", "q_declared": 2}]),
    "S3_ordinal_k2":     (_DF_ORD,  [{"name": "S3", "items": ["R1", "R2"],
                                       "data_type": "ordinal", "q_declared": 5, "scale_min": 1}]),
    "S4_ordinal_k4":     (_DF_ORD,  [{"name": "S4", "items": ["R1", "R2", "R3", "R4"],
                                       "data_type": "ordinal", "q_declared": 5, "scale_min": 1}]),
    "S5_interval_k2":    (_DF_IR,   [{"name": "S5", "items": ["R1", "R2"],
                                       "data_type": "interval"}]),
    "S6_interval_k4":    (_DF_IR,   [{"name": "S6", "items": ["R1", "R2", "R3", "R4"],
                                       "data_type": "interval"}]),
}

_OUT = {label: run_multi_irar(df, groups, n_boot=1000)["constructs"][0]
        for label, (df, groups) in _SCENARIOS.items()}


# ══════════════════════════════════════════════════════════════════════════
# 1. INDEPENDENT-LIBRARY CHECKS
# ══════════════════════════════════════════════════════════════════════════

def check_krippendorff_vs_independent_package():
    if not _HAVE_KD_PKG:
        _skip("Krippendorff alpha vs `krippendorff` package",
              "package not installed -- run: pip install krippendorff")
        return
    cases = [
        ("S1_dichotomous_k2", ["R1", "R2"],             "nominal"),
        ("S2_dichotomous_k4", ["R1", "R2", "R3", "R4"], "nominal"),
        ("S3_ordinal_k2",     ["R1", "R2"],             "ordinal"),
        ("S4_ordinal_k4",     ["R1", "R2", "R3", "R4"], "ordinal"),
        ("S5_interval_k2",    ["R1", "R2"],             "interval"),
        ("S6_interval_k4",    ["R1", "R2", "R3", "R4"], "interval"),
    ]
    for label, cols, level in cases:
        df, _ = _SCENARIOS[label]
        X = df[cols].to_numpy(dtype=float)
        ours = _OUT[label]["krippendorff"]["alpha"]
        ext = float(_kd_pkg.alpha(reliability_data=X.T, level_of_measurement=level))
        _check(f"Krippendorff alpha [{label}] vs krippendorff-pkg ({level})", ours, ext, tol=1e-6)
    # Also the ratio metric specifically (manuscript's interval/ratio samples
    # declared as ratio rather than interval)
    X_ratio = _DF_IR[["R1", "R2"]].to_numpy(dtype=float)
    from modules.reliability import _krippendorff_alpha
    ours_ratio, _ = _krippendorff_alpha(X_ratio, data_type="ratio", n_boot=0)
    ext_ratio = float(_kd_pkg.alpha(reliability_data=X_ratio.T, level_of_measurement="ratio"))
    _check("Krippendorff alpha [ratio metric, R1/R2] vs krippendorff-pkg", ours_ratio, ext_ratio, tol=1e-6)


def check_cohen_kappa_vs_sklearn():
    if not _HAVE_SKLEARN:
        _skip("Cohen's kappa vs scikit-learn", "scikit-learn not installed")
        return
    r1 = _DF_DICH["R1"].to_numpy()
    r2 = _DF_DICH["R2"].to_numpy()
    direct = float(_sklearn_kappa(r1, r2))
    ours = _OUT["S1_dichotomous_k2"]["cohen_kappa"]["kappa"]
    _check("Cohen's kappa [S1] vs direct scikit-learn call", ours, direct, tol=1e-9)


def check_icc_vs_pingouin():
    if not _HAVE_PINGOUIN:
        _skip("ICC(A,1) vs pingouin", "pingouin not installed")
        return
    sub = _DF_IR[["R1", "R2", "R3", "R4"]].dropna()
    n, k = sub.shape
    long = pd.DataFrame({
        "target": np.repeat(np.arange(n), k),
        "rater":  np.tile(np.arange(k), n),
        "score":  sub.to_numpy().flatten(),
    })
    direct_df = _pg.intraclass_corr(data=long, targets="target", raters="rater", ratings="score")
    direct = float(direct_df[direct_df["Type"] == "ICC(A,1)"]["ICC"].iloc[0])
    ours = _OUT["S6_interval_k4"]["icc"]["icc_2_1"]
    _check("ICC(A,1) [S6] vs direct pingouin call", ours, direct, tol=1e-9)


# ══════════════════════════════════════════════════════════════════════════
# 2. HAND-DERIVED CHECKS (formula re-typed from the manuscript's Method
#    details, independently of reliability.py's own _scott_pi/_brennan_
#    prediger/_gwet_ac1/_fleiss_kappa/_lin_ccc functions)
# ══════════════════════════════════════════════════════════════════════════

def check_scott_pi_hand():
    r1 = _DF_DICH["R1"].to_numpy(dtype=float)
    r2 = _DF_DICH["R2"].to_numpy(dtype=float)
    cats = sorted(set(r1.tolist()) | set(r2.tolist()))
    Po = float(np.mean(r1 == r2))
    Pe = sum(((np.mean(r1 == c) + np.mean(r2 == c)) / 2) ** 2 for c in cats)
    pi_hand = (Po - Pe) / (1 - Pe)
    ours = _OUT["S1_dichotomous_k2"]["scott_pi"]["pi"]
    _check("Scott's pi [S1] vs hand formula (Scott, 1955)", ours, pi_hand, tol=1e-9)


def check_brennan_prediger_hand():
    r1 = _DF_DICH["R1"].to_numpy(dtype=float)
    r2 = _DF_DICH["R2"].to_numpy(dtype=float)
    Po = float(np.mean(r1 == r2))
    q = 2
    Pe = 1.0 / q
    bp_hand = (Po - Pe) / (1 - Pe)
    ours = _OUT["S1_dichotomous_k2"]["brennan_prediger"]["kappa_bp"]
    _check("Brennan-Prediger [S1, q=2] vs hand formula (Brennan & Prediger, 1981)", ours, bp_hand, tol=1e-9)


def check_gwet_ac1_hand():
    r1 = _DF_DICH["R1"].to_numpy(dtype=float)
    r2 = _DF_DICH["R2"].to_numpy(dtype=float)
    q = 2
    Po = float(np.mean(r1 == r2))
    all_vals = np.concatenate([r1, r2])
    cats = sorted(set(all_vals.tolist()))
    pi_c = {c: np.mean(all_vals == c) for c in cats}
    Pe = (1.0 / (q - 1)) * sum(pi_c[c] * (1 - pi_c[c]) for c in cats)
    ac1_hand = (Po - Pe) / (1 - Pe)
    ours = _OUT["S1_dichotomous_k2"]["gwet_ac1"]["ac1"]
    _check("Gwet's AC1 [S1, q=2] vs hand formula (Gwet, 2008/2014, corrected (q-1) denom.)",
           ours, ac1_hand, tol=1e-9)


def check_fleiss_kappa_hand():
    X = _DF_DICH[["R1", "R2", "R3", "R4"]].dropna().to_numpy(dtype=float)
    n, k = X.shape
    cats = sorted(set(X.flatten().tolist()))
    table = np.zeros((n, len(cats)))
    for i in range(n):
        for j in range(k):
            table[i, cats.index(X[i, j])] += 1
    p_j = table.sum(axis=0) / (n * k)
    P_i = np.array([np.sum(table[i] * (table[i] - 1)) / (k * (k - 1)) for i in range(n)])
    P_bar = P_i.mean()
    P_e = np.sum(p_j ** 2)
    fleiss_hand = (P_bar - P_e) / (1 - P_e)
    ours = _OUT["S2_dichotomous_k4"]["fleiss_kappa"]["kappa"]
    _check("Fleiss' kappa [S2] vs hand formula (Fleiss, 1971)", ours, fleiss_hand, tol=1e-9)


def check_lin_ccc_hand():
    r1 = _DF_IR["R1"].to_numpy(dtype=float)
    r2 = _DF_IR["R2"].to_numpy(dtype=float)
    mx, my = r1.mean(), r2.mean()
    sx2, sy2 = r1.var(ddof=0), r2.var(ddof=0)
    sxy = np.cov(r1, r2, ddof=0)[0, 1]
    ccc_hand = 2 * sxy / (sx2 + sy2 + (mx - my) ** 2)
    ours = _OUT["S5_interval_k2"]["lin_ccc"]["ccc"]
    _check("Lin's CCC [S5] vs hand formula (Lin, 1989)", ours, ccc_hand, tol=1e-9)


# ══════════════════════════════════════════════════════════════════════════
# 3. STRUCTURAL-IDENTITY CHECKS
# ══════════════════════════════════════════════════════════════════════════

def check_ac2_identity_equals_ac1():
    from modules.reliability import _gwet_ac1
    X = _DF_ORD[["R1", "R2"]].dropna().to_numpy(dtype=float)
    ac1_direct = _gwet_ac1(X, q_declared=5)["ac1"]
    ac2_identity = _OUT["S3_ordinal_k2"]["gwet_ac2"]["schemes"]["identity"]["ac2"]
    _check("Gwet's AC2(identity weights) == Gwet's AC1 [S3, q=5] (required identity)",
           ac2_identity, ac1_direct, tol=1e-9)


# ══════════════════════════════════════════════════════════════════════════
# 4. REGRESSION CHECKS vs. the manuscript's own published S1-S6 tables
#    (Method validation, "End-to-end verification across all six
#    data-type x rater-count configurations"). Tolerance 5e-4 to allow for
#    the manuscript's 3-decimal rounding.
# ══════════════════════════════════════════════════════════════════════════

_PUBLISHED = {
    "S1_dichotomous_k2": {
        ("percentage_agreement", "pa"): 0.779,
        ("cohen_kappa", "kappa"): 0.413, ("cohen_kappa", "kappa_ase"): 0.107,
        ("scott_pi", "pi"): 0.411, ("scott_pi", "se"): 0.119,
        ("brennan_prediger", "kappa_bp"): 0.558, ("brennan_prediger", "se"): 0.089,
        ("gwet_ac1", "ac1"): 0.647, ("gwet_ac1", "se"): 0.083,
        ("krippendorff", "alpha"): 0.414,
    },
    "S2_dichotomous_k4": {
        ("percentage_agreement", "pa"): 0.806,
        ("fleiss_kappa", "kappa"): 0.437, ("fleiss_kappa", "kappa_se"): 0.044,
        ("gwet_ac1", "ac1"): 0.704, ("gwet_ac1", "se"): 0.052,
        ("krippendorff", "alpha"): 0.439,
    },
    "S3_ordinal_k2": {
        ("percentage_agreement", "pa"): 0.558,
        ("weighted_kappa", "kappa_linear"): 0.265,
        ("weighted_kappa", "kappa_quadratic"): 0.351,
        ("krippendorff", "alpha"): 0.316,
    },
    "S4_ordinal_k4": {
        ("percentage_agreement", "pa"): 0.579,
        ("krippendorff", "alpha"): 0.351,
    },
    "S5_interval_k2": {
        ("icc", "icc_1_1"): 0.383, ("icc", "icc_2_1"): 0.429, ("icc", "icc_3_1"): 0.504,
        ("lin_ccc", "ccc"): 0.426,
        ("krippendorff", "alpha"): 0.381,
    },
    "S6_interval_k4": {
        ("icc", "icc_1_1"): 0.528, ("icc", "icc_2_1"): 0.538, ("icc", "icc_3_1"): 0.590,
        ("krippendorff", "alpha"): 0.525,
    },
}

_AC2_PUBLISHED = {
    "S3_ordinal_k2": {"identity": 0.487, "linear": 0.805, "quadratic": 0.938,
                       "radical": 0.674, "ordinal": 0.708},
    "S4_ordinal_k4": {"identity": 0.510, "linear": 0.804, "quadratic": 0.931,
                       "radical": 0.682, "ordinal": 0.698},
}


def check_against_published_manuscript_tables():
    for label, fields in _PUBLISHED.items():
        res = _OUT[label]
        for (block, key), expected in fields.items():
            actual = (res.get(block) or {}).get(key)
            _check(f"[regression] {label}.{block}.{key} vs manuscript table", actual, expected, tol=5e-4)
    for label, schemes in _AC2_PUBLISHED.items():
        res = _OUT[label]
        for scheme, expected in schemes.items():
            actual = res["gwet_ac2"]["schemes"][scheme]["ac2"]
            _check(f"[regression] {label}.gwet_ac2.{scheme} vs manuscript table", actual, expected, tol=5e-4)


# ══════════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════════

def main():
    check_krippendorff_vs_independent_package()
    check_cohen_kappa_vs_sklearn()
    check_icc_vs_pingouin()
    check_scott_pi_hand()
    check_brennan_prediger_hand()
    check_gwet_ac1_hand()
    check_fleiss_kappa_hand()
    check_lin_ccc_hand()
    check_ac2_identity_equals_ac1()
    check_against_published_manuscript_tables()

    n_pass = sum(1 for _, s, _ in _RESULTS if s == "PASS")
    n_fail = sum(1 for _, s, _ in _RESULTS if s == "FAIL")
    n_skip = sum(1 for _, s, _ in _RESULTS if s == "SKIP")
    n_err  = sum(1 for _, s, _ in _RESULTS if s == "ERROR")

    width = max(len(name) for name, _, _ in _RESULTS)
    for name, status, detail in _RESULTS:
        print(f"[{status:5s}] {name:{width}s}  {detail}")

    print("-" * 80)
    print(f"{n_pass} passed, {n_fail} failed, {n_err} errored, {n_skip} skipped "
          f"(of {len(_RESULTS)} checks)")

    if n_fail or n_err:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
