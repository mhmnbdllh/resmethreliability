"""
tests/test_irar_formulas.py
============================
Permanent, re-runnable correctness checks for every Inter-Rater Agreement
(ResMeth-IRA) coefficient computed by modules/reliability.py.

Five kinds of check are used, because they catch different kinds of error:

  1. INDEPENDENT-LIBRARY checks -- the application's output is compared with
     independent implementations: the `krippendorff` package (Krippendorff's
     alpha, four metrics, with and without missing data), scikit-learn
     (Cohen's kappa, unweighted and weighted), statsmodels (the Fleiss,
     Cohen & Everitt (1969) standard errors of kappa) and pingouin (the six
     ICC forms and their 95% confidence intervals).
  2. HAND-DERIVED checks -- each coefficient, standard error and interval is
     recomputed in THIS file from the raw rating columns with numpy only,
     from the formula in its primary source, never by calling the module's
     own coefficient helpers.
  3. STRUCTURAL checks -- AC2 with identity weights must equal AC1; the
     bootstrap interval of Krippendorff's alpha must be reproducible; every
     interval must widen as the confidence level rises.
  4. PUBLISHED-EXAMPLE checks -- numerical examples printed in primary
     sources are reproduced at the precision printed there: Fleiss, Cohen &
     Everitt (1969; kappa and its two variances), Fleiss (1971; overall and
     category kappas), Shrout & Fleiss (1979; six ICCs) and Krippendorff
     (2011; alpha under four metrics, with missing values).
  5. REGRESSION checks -- the values reported in the accompanying article's
     tables (three decimals) must still be produced.

HOW TO RUN
----------
    pip install -r tests/requirements-test.txt     # krippendorff, statsmodels
    python3 tests/test_irar_formulas.py

A missing optional package makes its checks SKIP (reported, never silently
passed). Exit code 0 if every check passed, 1 otherwise.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
from scipy import stats

from modules.reliability import run_multi_irar

try:
    import krippendorff as _kd_pkg
except ImportError:
    _kd_pkg = None
try:
    from sklearn.metrics import cohen_kappa_score as _sk_kappa
except ImportError:
    _sk_kappa = None
try:
    import statsmodels.stats.inter_rater as _smir
except ImportError:
    _smir = None
try:
    import pingouin as _pg
except ImportError:
    _pg = None

_RESULTS = []


def _check(name, a, b, tol):
    try:
        diff = abs(float(a) - float(b))
        _RESULTS.append((name, "PASS" if diff <= tol else "FAIL",
                         f"app={float(a):.10g} ref={float(b):.10g} diff={diff:.2e} tol={tol:.0e}"))
    except Exception as e:
        _RESULTS.append((name, "ERROR", f"{type(e).__name__}: {e}"))


def _true(name, cond, detail=""):
    _RESULTS.append((name, "PASS" if cond else "FAIL", detail))


def _skip(name, why):
    _RESULTS.append((name, "SKIP", why))


# ══════════════════════════════════════════════════════════════════════════
# Data and the six configurations (data type x number of raters)
# ══════════════════════════════════════════════════════════════════════════

_DICH = pd.read_csv(_ROOT / "sample-resmeth_Dichotomous.csv")
_ORD = pd.read_csv(_ROOT / "sample-resmeth_Nominal-Ordinal.csv")
_IR = pd.read_csv(_ROOT / "sample-resmeth_Interval-Ratio.csv")
_ALL = ["R1", "R2", "R3", "R4"]
_TWO = ["R1", "R2"]

_GROUPS = {
    "S1": (_DICH, {"items": _TWO, "data_type": "dichotomous", "q_declared": 2}),
    "S2": (_DICH, {"items": _ALL, "data_type": "dichotomous", "q_declared": 2}),
    "S3": (_ORD, {"items": _TWO, "data_type": "ordinal", "q_declared": 5, "scale_min": 1}),
    "S4": (_ORD, {"items": _ALL, "data_type": "ordinal", "q_declared": 5, "scale_min": 1}),
    "S5": (_IR, {"items": _TWO, "data_type": "interval"}),
    "S6": (_IR, {"items": _ALL, "data_type": "interval"}),
}


def _run(label, alpha=0.05, n_boot=1000, df=None):
    base, grp = _GROUPS[label]
    g = dict(grp, name=label)
    return run_multi_irar(base if df is None else df, [g], alpha=alpha, n_boot=n_boot)["constructs"][0]


_OUT = {lab: _run(lab) for lab in _GROUPS}


def _X(label):
    base, grp = _GROUPS[label]
    return base[grp["items"]].to_numpy(dtype=float)


# ══════════════════════════════════════════════════════════════════════════
# 1. Independent-library checks
# ══════════════════════════════════════════════════════════════════════════

def check_krippendorff_package():
    if _kd_pkg is None:
        _skip("Krippendorff alpha vs krippendorff package", "pip install krippendorff")
        return
    from modules.reliability import _krippendorff_alpha
    level = {"S1": "nominal", "S2": "nominal", "S3": "ordinal", "S4": "ordinal",
             "S5": "interval", "S6": "interval"}
    for lab, lv in level.items():
        _check(f"alpha {lab} ({lv}) vs krippendorff pkg", _OUT[lab]["krippendorff"]["alpha"],
               _kd_pkg.alpha(reliability_data=_X(lab).T, level_of_measurement=lv), 1e-10)
    a_ratio, _ = _krippendorff_alpha(_X("S6"), "ratio", n_boot=0)
    _check("alpha S6 (ratio) vs krippendorff pkg", a_ratio,
           _kd_pkg.alpha(reliability_data=_X("S6").T, level_of_measurement="ratio"), 1e-10)
    rng = np.random.default_rng(7)
    for lab, lv in (("S2", "nominal"), ("S4", "ordinal"), ("S6", "interval")):
        Xm = _X(lab).copy()
        Xm[rng.random(Xm.shape) < 0.10] = np.nan
        base, _ = _GROUPS[lab]
        res = _run(lab, n_boot=200, df=pd.DataFrame(Xm, columns=_ALL))
        _check(f"alpha {lab} with 10% missing cells vs krippendorff pkg", res["krippendorff"]["alpha"],
               _kd_pkg.alpha(reliability_data=Xm.T, level_of_measurement=lv), 1e-10)
        _true(f"alpha {lab} with missing cells uses more units than listwise deletion",
              res["krippendorff"]["n_units"] > res["n_units"],
              f"alpha units={res['krippendorff']['n_units']} listwise units={res['n_units']}")


def check_kappa_libraries():
    if _sk_kappa is None:
        _skip("Cohen's kappa vs scikit-learn", "scikit-learn not installed")
    else:
        x = _X("S1").astype(int)
        _check("Cohen kappa S1 vs scikit-learn", _OUT["S1"]["cohen_kappa"]["kappa"],
               _sk_kappa(x[:, 0], x[:, 1]), 1e-12)
        x = _X("S3").astype(int)
        for sch in ("linear", "quadratic"):
            _check(f"weighted kappa ({sch}) S3 vs scikit-learn (labels 1..5)",
                   _OUT["S3"]["weighted_kappa"]["variants"][sch]["kappa"],
                   _sk_kappa(x[:, 0], x[:, 1], weights=sch, labels=[1, 2, 3, 4, 5]), 1e-12)
    if _smir is None:
        _skip("kappa standard errors vs statsmodels", "pip install statsmodels")
        return
    for lab, block, cats in (("S1", "cohen_kappa", [0, 1]), ("S3", "weighted_kappa", [1, 2, 3, 4, 5])):
        x = _X(lab).astype(int)
        T = np.zeros((len(cats), len(cats)))
        for a, b in x:
            T[cats.index(a), cats.index(b)] += 1
        for sch, wt in (("unweighted", None), ("linear", "linear"), ("quadratic", "quadratic")):
            if lab == "S1" and wt is not None:
                continue
            sm = (_smir.cohens_kappa(T, return_results=True) if wt is None else
                  _smir.cohens_kappa(T, weights=np.arange(len(cats)), wt=wt, return_results=True))
            v = _OUT[lab][block]["variants"][sch]
            _check(f"kappa {sch} {lab}: null SE (Eq. 9) vs statsmodels", v["se_null"], sm.std_kappa0, 1e-10)
            _check(f"kappa {sch} {lab}: general SE (Eq. 8) vs statsmodels", v["se_general"], sm.std_kappa, 1e-10)


def check_icc_pingouin():
    if _pg is None:
        _skip("ICC vs pingouin", "pingouin not installed")
        return
    names = {"1_1": "ICC(1,1)", "2_1": "ICC(A,1)", "3_1": "ICC(C,1)",
             "1_k": "ICC(1,k)", "2_k": "ICC(A,k)", "3_k": "ICC(C,k)"}
    for lab in ("S5", "S6"):
        X = _X(lab)
        n, k = X.shape
        long = pd.DataFrame({"t": np.repeat(np.arange(n), k), "r": np.tile(np.arange(k), n),
                             "s": X.flatten()})
        ref = _pg.intraclass_corr(data=long, targets="t", raters="r", ratings="s")
        ref["Type"] = ref["Type"].replace({"ICC1": "ICC(1,1)", "ICC2": "ICC(A,1)", "ICC3": "ICC(C,1)",
                                           "ICC1k": "ICC(1,k)", "ICC2k": "ICC(A,k)", "ICC3k": "ICC(C,k)"})
        ref = ref.set_index("Type")
        ci_col = "CI95" if "CI95" in ref.columns else "CI95%"
        for key, t in names.items():
            _check(f"{t} {lab} vs pingouin", _OUT[lab]["icc"][f"icc_{key}"], ref.loc[t, "ICC"], 1e-10)
            # pingouin prints its 95% bounds to two decimals
            for side, j in (("lo", 0), ("hi", 1)):
                _check(f"{t} {lab} 95% CI {side} vs pingouin (2 dp)",
                       round(_OUT[lab]["icc"][f"icc_{key}_ci_{side}"], 2), ref.loc[t, ci_col][j], 1e-12)


# ══════════════════════════════════════════════════════════════════════════
# 2. Hand-derived checks
# ══════════════════════════════════════════════════════════════════════════

def _pairs_agree(X):
    n, k = X.shape
    return np.array([np.mean([X[i, a] == X[i, b] for a in range(k) for b in range(a + 1, k)])
                     for i in range(n)])


def check_percentage_agreement():
    for lab in _GROUPS:
        per = _pairs_agree(_X(lab))
        n = len(per)
        pa, se = per.mean(), per.std(ddof=1) / np.sqrt(n)
        t = stats.t.ppf(0.975, n - 1)
        r = _OUT[lab]["percentage_agreement"]
        _check(f"PA {lab}", r["pa"], pa, 1e-12)
        _check(f"PA {lab} CI lower (unit-level t)", r["ci_lo"], max(0.0, pa - t * se), 1e-12)
        _check(f"PA {lab} CI upper (unit-level t)", r["ci_hi"], min(1.0, pa + t * se), 1e-12)


def check_two_rater_nominal():
    x = _X("S1")
    r1, r2 = x[:, 0], x[:, 1]
    n = len(r1)
    po = np.mean(r1 == r2)
    p1 = np.array([np.mean(r1 == c) for c in (0, 1)])
    p2 = np.array([np.mean(r2 == c) for c in (0, 1)])
    pe_c, pe_s, pe_b = (p1 * p2).sum(), (((p1 + p2) / 2) ** 2).sum(), 0.5
    _check("Cohen kappa S1 (Cohen, 1960)", _OUT["S1"]["cohen_kappa"]["kappa"], (po - pe_c) / (1 - pe_c), 1e-12)
    cv = _OUT["S1"]["cohen_kappa"]["variants"]["unweighted"]
    zc = stats.norm.ppf(0.975)
    _check("Cohen kappa S1 CI lower (z, general SE Eq. 8)", cv["ci_lo_z"], cv["kappa"] - zc * cv["se_general"], 1e-12)
    _check("Cohen kappa S1 CI upper (z, general SE Eq. 8)", cv["ci_hi_z"], cv["kappa"] + zc * cv["se_general"], 1e-12)
    sp = _OUT["S1"]["scott_pi"]
    _check("Scott pi S1 (Scott, 1955)", sp["pi"], (po - pe_s) / (1 - pe_s), 1e-12)
    # Scott's pi = Fleiss' kappa with two raters: null SE (Fleiss, Nee &
    # Landis, 1979) and general SE (Gwet, 2021, Eqs. 4 and 12).
    pbar = (p1 + p2) / 2
    s1, s2 = np.sum(pbar * (1 - pbar)), np.sum(pbar * (1 - pbar) * (1 - 2 * pbar))
    se0 = np.sqrt(2 / (n * 2 * 1 * s1 ** 2) * (s1 ** 2 - s2))
    pi_hat = (po - pe_s) / (1 - pe_s)
    agree = (r1 == r2).astype(float)
    pe_unit = np.array([(pbar[int(a)] + pbar[int(b)]) / 2 for a, b in zip(r1, r2)])
    k_star = (agree - pe_s) / (1 - pe_s) - 2 * (1 - pi_hat) * (pe_unit - pe_s) / (1 - pe_s)
    se_g = np.sqrt(np.sum((k_star - pi_hat) ** 2) / (n * (n - 1)))
    _check("Scott pi S1 SE under H0 (Fleiss, Nee & Landis, 1979; k=2)", sp["se_null"], se0, 1e-12)
    _check("Scott pi S1 general SE (Gwet, 2021; k=2)", sp["se"], se_g, 1e-12)
    _check("Scott pi S1 t-interval upper (df=n-1)", sp["ci_hi_t"], pi_hat + stats.t.ppf(0.975, n - 1) * se_g, 1e-12)
    _check("Scott pi S1 z uses the null SE", sp["z"], pi_hat / se0, 1e-12)
    bp = _OUT["S1"]["brennan_prediger"]
    _check("Brennan-Prediger S1 (q=2)", bp["kappa_bp"], (po - pe_b) / (1 - pe_b), 1e-12)
    _check("Brennan-Prediger S1 SE", bp["se"], np.sqrt(po * (1 - po) / (n * (1 - pe_b) ** 2)), 1e-12)
    z, t = stats.norm.ppf(0.975), stats.t.ppf(0.975, n - 1)
    _check("Brennan-Prediger S1 z-interval lower", bp["ci_lo_z"], bp["kappa_bp"] - z * bp["se"], 1e-12)
    _check("Brennan-Prediger S1 t-interval upper", bp["ci_hi_t"], bp["kappa_bp"] + t * bp["se"], 1e-12)


def _ac1(X, cats):
    po = _pairs_agree(X).mean()
    pi = np.array([np.mean(X == c) for c in cats])
    pe = np.sum(pi * (1 - pi)) / (len(cats) - 1)
    return (po - pe) / (1 - pe)


def check_gwet_ac1():
    for lab in ("S1", "S2"):
        X = _X(lab)
        n = len(X)
        est = _ac1(X, [0, 1])
        jk = np.array([_ac1(np.delete(X, i, 0), [0, 1]) for i in range(n)])
        se = np.sqrt((n - 1) / n * np.sum((jk - jk.mean()) ** 2))
        r = _OUT[lab]["gwet_ac1"]
        _check(f"Gwet AC1 {lab} (Gwet, 2008; (q-1) denominator)", r["ac1"], est, 1e-12)
        _check(f"Gwet AC1 {lab} jackknife SE", r["se"], se, 1e-12)


def _gwet_weights(scheme, q):
    i = np.arange(q)
    d = np.abs(i[:, None] - i[None, :]).astype(float)
    if scheme == "identity":
        return np.eye(q)
    if scheme == "linear":
        return 1 - d / (q - 1)
    if scheme == "quadratic":
        return 1 - d ** 2 / (q - 1) ** 2
    if scheme == "radical":
        return 1 - np.sqrt(d / (q - 1))
    m = (d + 1) * d / 2          # ordinal: number of category pairs spanned
    return 1 - m / m.max()


def _ac2(X, scheme, lo=1, q=5):
    W = _gwet_weights(scheme, q)
    n, k = X.shape
    pw = np.mean([np.mean([W[int(X[i, a]) - lo, int(X[i, b]) - lo] for a in range(k) for b in range(a + 1, k)])
                  for i in range(n)])
    pi = np.array([np.mean(X == lo + c) for c in range(q)])
    pe = W.sum() * np.sum(pi * (1 - pi)) / (q * (q - 1))
    return (pw - pe) / (1 - pe)


def check_gwet_ac2():
    for lab in ("S3", "S4"):
        X = _X(lab)
        for sch in ("identity", "linear", "quadratic", "radical", "ordinal"):
            _check(f"Gwet AC2 [{sch}] {lab} (Gwet, 2014)", _OUT[lab]["gwet_ac2"]["schemes"][sch]["ac2"],
                   _ac2(X, sch), 1e-12)


def check_fleiss():
    X = _X("S2").astype(int)
    n, k = X.shape
    cats = sorted(set(X.flatten()))
    tab = np.array([[np.sum(X[i] == c) for c in cats] for i in range(n)], dtype=float)
    p = tab.sum(0) / (n * k)
    pbar = np.mean((tab * (tab - 1)).sum(1) / (k * (k - 1)))
    pe = np.sum(p ** 2)
    pq = p * (1 - p)
    var0 = 2 / (n * k * (k - 1)) * (pq.sum() ** 2 - np.sum(pq * (1 - 2 * p))) / pq.sum() ** 2
    r = _OUT["S2"]["fleiss_kappa"]
    kap = (pbar - pe) / (1 - pe)
    _check("Fleiss kappa S2 (Fleiss, 1971)", r["kappa"], kap, 1e-12)
    _check("Fleiss kappa S2 null SE (Fleiss, Nee & Landis, 1979)", r["kappa_se"], np.sqrt(var0), 1e-12)
    pa_i = (tab * (tab - 1)).sum(1) / (k * (k - 1))
    pe_i = (tab * p).sum(1) / k
    kstar = (pa_i - pe) / (1 - pe) - 2 * (1 - kap) * (pe_i - pe) / (1 - pe)
    se_g = np.sqrt(np.sum((kstar - kap) ** 2) / (n * (n - 1)))
    _check("Fleiss kappa S2 general SE (Gwet, 2021, Eqs. 4-6)", r["kappa_se_general"], se_g, 1e-12)
    t = stats.t.ppf(0.975, n - 1)
    _check("Fleiss kappa S2 CI lower (t-basis)", r["ci_lo_t"], kap - t * se_g, 1e-12)
    _check("Fleiss kappa S2 CI upper (t-basis)", r["ci_hi_t"], kap + t * se_g, 1e-12)


def check_lin_ccc():
    x, y = _X("S5")[:, 0], _X("S5")[:, 1]
    n = len(x)
    mx, my, sx2, sy2 = x.mean(), y.mean(), x.var(), y.var()
    sxy = np.mean((x - mx) * (y - my))
    c = 2 * sxy / (sx2 + sy2 + (mx - my) ** 2)
    r = np.corrcoef(x, y)[0, 1]
    u = (mx - my) / (sx2 * sy2) ** 0.25
    vz = ((1 - r ** 2) * c ** 2 / ((1 - c ** 2) * r ** 2) + 2 * c ** 3 * (1 - c) * u ** 2 / (r * (1 - c ** 2) ** 2)
          - c ** 4 * u ** 4 / (2 * r ** 2 * (1 - c ** 2) ** 2)) / (n - 2)
    z = stats.norm.ppf(0.975)
    res = _OUT["S5"]["lin_ccc"]
    _check("Lin CCC S5 (Lin, 1989)", res["ccc"], c, 1e-12)
    _check("Lin CCC S5 CI lower (Fisher z, Lin 1989/2000 variance)", res["ci_lo"], np.tanh(np.arctanh(c) - z * np.sqrt(vz)), 1e-12)
    _check("Lin CCC S5 CI upper", res["ci_hi"], np.tanh(np.arctanh(c) + z * np.sqrt(vz)), 1e-12)


# ══════════════════════════════════════════════════════════════════════════
# 3. Structural checks
# ══════════════════════════════════════════════════════════════════════════

def check_structure():
    from modules.reliability import _gwet_ac1, _krippendorff_alpha
    _check("AC2(identity) == AC1 [S3, q=5]", _OUT["S3"]["gwet_ac2"]["schemes"]["identity"]["ac2"],
           _gwet_ac1(_X("S3"), q_declared=5)["ac1"], 1e-12)
    a1 = _krippendorff_alpha(_X("S4"), "ordinal", n_boot=500)
    a2 = _krippendorff_alpha(_X("S4"), "ordinal", n_boot=500)
    _true("Krippendorff bootstrap CI reproducible (fixed seed)", a1 == a2, str(a1))
    widths = {}
    for a in (0.10, 0.05, 0.01):
        o1, o5 = _run("S1", alpha=a, n_boot=1000), _run("S5", alpha=a, n_boot=1000)
        widths[a] = (o1["percentage_agreement"]["ci_hi"] - o1["percentage_agreement"]["ci_lo"],
                     o1["gwet_ac1"]["ci_hi_z"] - o1["gwet_ac1"]["ci_lo_z"],
                     o1["krippendorff"]["ci_hi"] - o1["krippendorff"]["ci_lo"],
                     o5["icc"]["icc_2_1_ci_hi"] - o5["icc"]["icc_2_1_ci_lo"],
                     o5["lin_ccc"]["ci_hi"] - o5["lin_ccc"]["ci_lo"])
    for j, nm in enumerate(("PA", "AC1", "Krippendorff alpha", "ICC(A,1)", "Lin CCC")):
        _true(f"{nm}: interval widens 90% < 95% < 99%", widths[0.10][j] < widths[0.05][j] < widths[0.01][j],
              f"{widths[0.10][j]:.4f} < {widths[0.05][j]:.4f} < {widths[0.01][j]:.4f}")


# ══════════════════════════════════════════════════════════════════════════
# 4. Regression checks against the values reported in the article's tables
# ══════════════════════════════════════════════════════════════════════════

_REPORTED = {
    "S1": {("percentage_agreement", "pa"): 0.779, ("cohen_kappa", "kappa"): 0.413,
           ("scott_pi", "pi"): 0.411, ("brennan_prediger", "kappa_bp"): 0.558,
           ("gwet_ac1", "ac1"): 0.647, ("krippendorff", "alpha"): 0.414},
    "S2": {("percentage_agreement", "pa"): 0.806, ("fleiss_kappa", "kappa"): 0.437,
           ("gwet_ac1", "ac1"): 0.704, ("krippendorff", "alpha"): 0.439},
    "S3": {("percentage_agreement", "pa"): 0.558, ("weighted_kappa", "kappa_linear"): 0.265,
           ("weighted_kappa", "kappa_quadratic"): 0.351, ("krippendorff", "alpha"): 0.316},
    "S4": {("percentage_agreement", "pa"): 0.579, ("krippendorff", "alpha"): 0.351},
    "S5": {("icc", "icc_2_1"): 0.429, ("icc", "icc_3_1"): 0.504, ("lin_ccc", "ccc"): 0.426,
           ("krippendorff", "alpha"): 0.381},
    "S6": {("icc", "icc_2_1"): 0.538, ("icc", "icc_3_1"): 0.590, ("krippendorff", "alpha"): 0.525},
}
_REPORTED_AC2 = {
    "S3": {"identity": 0.487, "linear": 0.805, "quadratic": 0.938, "radical": 0.674, "ordinal": 0.907},
    "S4": {"identity": 0.510, "linear": 0.804, "quadratic": 0.931, "radical": 0.682, "ordinal": 0.901},
}


def check_published_examples():
    """Numerical examples printed in the primary sources, reproduced at the
    precision printed there."""
    from modules.reliability import _kappa_se_z_p_exact
    # Fleiss, Cohen & Everitt (1969): N = 200, proportions x 200.
    t = np.array([[106, 10, 4], [22, 28, 10], [2, 12, 6]], dtype=float)
    u = _kappa_se_z_p_exact(t, np.eye(3))
    _check("[published] FCE 1969 kappa = .429", u["kappa"], 0.429, 5e-4)
    _check("[published] FCE 1969 general variance = .002885", u["se_general"] ** 2, 0.002885, 5e-7)
    _check("[published] FCE 1969 null variance = .003082", u["se_null"] ** 2, 0.003082, 5e-7)
    W = np.array([[1, 0, 4 / 9], [0, 1, 2 / 3], [4 / 9, 2 / 3, 1]])
    P = t / t.sum()
    _check("[published] FCE 1969 weighted p_o = .787", (W * P).sum(), 0.787, 5e-4)
    _check("[published] FCE 1969 weighted p_e = .567", (W * np.outer(P.sum(1), P.sum(0))).sum(), 0.567, 5e-4)
    # Fleiss (1971): 30 patients x 6 psychiatrists, 5 categories.
    diag = np.array([
        [4, 4, 4, 4, 4, 4], [2, 2, 2, 5, 5, 5], [2, 3, 3, 3, 3, 5], [5, 5, 5, 5, 5, 5],
        [2, 2, 2, 4, 4, 4], [1, 1, 3, 3, 3, 3], [3, 3, 3, 3, 5, 5], [1, 1, 3, 3, 3, 4],
        [1, 1, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [1, 4, 4, 4, 4, 4], [1, 2, 4, 4, 4, 4],
        [2, 2, 2, 3, 3, 3], [1, 4, 4, 4, 4, 4], [2, 2, 4, 4, 4, 5], [3, 3, 3, 3, 3, 5],
        [1, 1, 1, 4, 5, 5], [1, 1, 1, 1, 1, 2], [2, 2, 4, 4, 4, 4], [1, 3, 3, 5, 5, 5],
        [5, 5, 5, 5, 5, 5], [2, 4, 4, 4, 4, 4], [2, 2, 4, 5, 5, 5], [1, 1, 4, 4, 4, 4],
        [1, 4, 4, 4, 4, 5], [2, 2, 2, 2, 2, 4], [1, 1, 1, 1, 5, 5], [2, 2, 4, 4, 4, 4],
        [1, 3, 3, 3, 3, 3], [5, 5, 5, 5, 5, 5]])
    cols = [f"P{i}" for i in range(1, 7)]
    fk = run_multi_irar(pd.DataFrame(diag, columns=cols),
                        [{"name": "F71", "items": cols, "data_type": "nominal", "q_declared": 5}],
                        n_boot=0)["constructs"][0]["fleiss_kappa"]
    _check("[published] Fleiss 1971 kappa = .430", fk["kappa"], 0.430, 5e-4)
    for cat, val in {1: 0.245, 2: 0.245, 3: 0.520, 4: 0.471, 5: 0.566}.items():
        _check(f"[published] Fleiss 1971 category {cat} kappa = {val:.3f}", fk["kappa_per_category"][cat], val, 5e-4)
    # Shrout & Fleiss (1979): 6 targets x 4 judges.
    sf = pd.DataFrame([[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]],
                      columns=["J1", "J2", "J3", "J4"], dtype=float)
    ic = run_multi_irar(sf, [{"name": "SF79", "items": list(sf.columns), "data_type": "interval"}],
                        n_boot=0)["constructs"][0]["icc"]
    for key, lab, val in (("icc_1_1", "ICC(1,1)", 0.17), ("icc_2_1", "ICC(2,1)", 0.29), ("icc_3_1", "ICC(3,1)", 0.71),
                          ("icc_1_k", "ICC(1,4)", 0.44), ("icc_2_k", "ICC(2,4)", 0.62), ("icc_3_k", "ICC(3,4)", 0.91)):
        _check(f"[published] Shrout & Fleiss 1979 {lab} = {val:.2f}", ic[key], val, 5e-3)
    # Krippendorff (2011): 12 units x 4 observers with missing values.
    nan = np.nan
    K = pd.DataFrame(np.array([
        [1, 2, 3, 3, 2, 1, 4, 1, 2, nan, nan, nan],
        [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, nan, 3],
        [nan, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, nan],
        [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, nan]]).T, columns=["A", "B", "C", "D"])
    for dt, val in (("nominal", 0.743), ("ordinal", 0.815), ("interval", 0.849), ("ratio", 0.797)):
        g = {"name": dt, "items": list(K.columns), "data_type": dt}
        if dt == "nominal":
            g["q_declared"] = 5
        if dt == "ordinal":
            g.update(q_declared=5, scale_min=1)
        a = run_multi_irar(K, [g], n_boot=0)["constructs"][0]["krippendorff"]["alpha"]
        _check(f"[published] Krippendorff 2011 alpha ({dt}) = {val:.3f}", a, val, 5e-4)


def check_reported_values():
    for lab, fields in _REPORTED.items():
        for (block, key), val in fields.items():
            _check(f"[reported] {lab} {block}.{key}", (_OUT[lab].get(block) or {}).get(key), val, 5e-4)
    for lab, sch in _REPORTED_AC2.items():
        for s, val in sch.items():
            _check(f"[reported] {lab} AC2 {s}", _OUT[lab]["gwet_ac2"]["schemes"][s]["ac2"], val, 5e-4)


def main():
    for fn in (check_krippendorff_package, check_kappa_libraries, check_icc_pingouin,
               check_percentage_agreement, check_two_rater_nominal, check_gwet_ac1,
               check_gwet_ac2, check_fleiss, check_lin_ccc, check_structure, check_published_examples,
               check_reported_values):
        try:
            fn()
        except Exception as e:
            _RESULTS.append((fn.__name__, "ERROR", f"{type(e).__name__}: {e}"))
    width = max(len(r[0]) for r in _RESULTS)
    for name, status, detail in _RESULTS:
        print(f"[{status:5s}] {name:{width}s}  {detail}")
    counts = {s: sum(1 for r in _RESULTS if r[1] == s) for s in ("PASS", "FAIL", "ERROR", "SKIP")}
    print("-" * 80)
    print(f"{counts['PASS']} passed, {counts['FAIL']} failed, {counts['ERROR']} errored, "
          f"{counts['SKIP']} skipped (of {len(_RESULTS)} checks)")
    ok = counts["FAIL"] == 0 and counts["ERROR"] == 0
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
