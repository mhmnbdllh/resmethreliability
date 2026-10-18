"""
pages/6_reliability.py
======================
Streamlit page for Reliability Analysis (internal consistency).

One file, multiple constructs. Each construct gets its own tab; within a
construct, every reliability coefficient has its own sub-tab with key-info
cards, the relevant table(s), the decision parameters, an automatic descriptive
interpretation, and a contextual note. A full Item Statistics sub-tab (incl.
Median and extended descriptives), Summary Item Statistics, Item-Total Statistics
(with the negative-value footnote), Inter-Item Correlation matrix, and
Scale Statistics are included. The same content is exported to HTML and CSV.
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Reliability | Inferential Statistics by Muhaimin Abdullah",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles      import load_page_css
from utils.file_loader import (load_file, load_from_string, validate_file,
                                file_metadata, get_numeric_cols)
from utils.samples     import SAMPLES
from utils.formatters  import _f as _f_base, _p as _p_base
from utils.tables      import html_tbl
from utils.plots       import fig_to_bytes

from modules.reliability import (run_multi_reliability, run_multi_irar,
                                  alpha_label)

# ── Reliability-module display precision ───────────────────────────────
# All Reliability output (Web UI, HTML export, CSV export) is displayed
# to 4 decimal places, distinct from other modules' 3-decimal convention.
# CORRECTED: an earlier "5 decimal places" target was found to be
# cosmetic only — the engine prematurely rounded most coefficients to
# 3-4dp internally (see reliability.py, systematic de-rounding pass),
# so the 4th/5th displayed digits were architecturally guaranteed to be
# padding zeros, not genuinely computed values. The engine now preserves
# full floating-point precision throughout; 4dp here reflects genuinely
# computed digits, not padding. Shadowing _f/_p locally (rather than
# changing formatters.py's default) keeps this a Reliability-only change
# with zero effect on other modules that import the same shared
# formatters.
def _f(v, d=4):
    return _f_base(v, d)

def _p(v, d=4):
    return _p_base(v, d)

# ── Canonical formatters (Fresh-Eyes audit consolidation) ───────────────
# Previously 4 byte-for-byte-identical CI formatters (_ci2, _ci3, _ci3s,
# _ci_s) and 3 byte-for-byte-identical p-value formatters (_icc_p, _ps,
# _icc_p_irar) were independently defined as local closures in different
# rendering blocks. Per Fresh-Eyes Audit Protocol Aturan 3: functions
# that are 100% identical in body are consolidated into one definition,
# called wherever needed, rather than re-implemented per call site.
# (Reformatted to 5 decimal places while consolidating, consistent with
# the rest of this module's display precision.)
def _fmt_ci(lo, hi):
    """Bracket-formatted confidence interval, e.g. '[0.47000, 0.80000]'."""
    try:
        return (f"[{_f(float(lo))}, {_f(float(hi))}]"
                if not (np.isnan(float(lo)) or np.isnan(float(hi))) else "\u2014")
    except Exception:
        return "\u2014"

def _fmt_p_dash(p):
    """p-value formatted via the canonical _p() threshold-aware formatter,
    with '\u2014' (em dash) for missing/NaN instead of _p()'s own '.'
    convention -- distinguishes 'not applicable in this table' from the
    general numeric-missing convention used elsewhere."""
    try:
        if p is None or (isinstance(p, float) and np.isnan(p)):
            return "\u2014"
        return _p(float(p))
    except Exception:
        return "\u2014"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAL = ["#1a1a2e", "#e94560", "#0f3460", "#16213e"]
BG  = "#f8fafc"


# ══════════════════════════════════════════════════════════════════════════════
# INTERPRETATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _icc_label(v):
    """Koo & Li (2016) interpretation for ICC."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "undefined"
    if v < 0.5:
        return "poor"
    if v < 0.75:
        return "moderate"
    if v < 0.90:
        return "good"
    return "excellent"


def _coeff_blocks(res, alpha):
    """Ordered per-coefficient blocks shared by web/HTML/CSV.

    Each block: dict(key, title, cards=[(label,value,sub)], table=(cols,rows)|None,
                      params, interp, note)
    """
    pct = int((1 - res.get("alpha_level", alpha)) * 100)
    a = res.get("alpha"); ci = res.get("alpha_ci", (np.nan, np.nan))
    a_std = res.get("alpha_std"); omega = res.get("omega")
    omh = res.get("omega_h_detail") or {}
    lam = res.get("lambdas", {}); sh = res.get("split_half", {})
    kr = res.get("kr20"); dich = res.get("dichotomous")
    k = res["k"]; n = res["n"]
    blocks = []

    a_neg = (a is not None and not (isinstance(a, float) and np.isnan(a)) and a < 0) or \
            (a_std is not None and not (isinstance(a_std, float) and np.isnan(a_std)) and a_std < 0)
    blocks.append({
        "key": "Alpha", "title": "Cronbach's Alpha",
        "cards": [("Cronbach's \u03b1", _f(a), alpha_label(a)),
                  (f"{pct}% CI", f"[{_f(ci[0])}, {_f(ci[1])}]", "Feldt method"),
                  ("Standardised \u03b1", _f(a_std), "from correlations")],
        "table": (["Cronbach's Alpha" + ("\u1d43" if a_neg else ""),
                   "Cronbach's Alpha Based on Standardized Items" + ("\u1d43" if a_neg else ""),
                   f"{pct}% CI", "N of Items"],
                  [[_f(a), _f(a_std), f"[{_f(ci[0])}, {_f(ci[1])}]", str(k)]]),
        "table_left": set(),
        "footnote": ("a. The value is negative due to a negative average covariance "
                     "among items. This violates reliability model assumptions. You "
                     "may want to check item codings.") if a_neg else "",
        "params": ("Thresholds (George &amp; Mallery, 2003): \u2265.9 excellent, "
                   ".8\u2013.89 good, .7\u2013.79 acceptable, .6\u2013.69 questionable, "
                   ".5\u2013.59 poor, &lt;.5 unacceptable."),
        "interp": (f"Cronbach\u2019s alpha = {_f(a)}, indicating <b>{alpha_label(a)}</b> "
                   f"internal consistency for {k} items (N = {n}). The {pct}% "
                   f"confidence interval is [{_f(ci[0])}, {_f(ci[1])}]."
                   + (" A negative value indicates a negative average inter-item "
                      "covariance \u2014 check for reverse-scored items." if a_neg else "")),
        "note": ("Alpha assumes (essentially) tau-equivalent items and "
                 "unidimensionality; it is a lower bound to true reliability."),
    })

    # ── McDonald's Omega: ONE tab, TWO clearly-headed sections ─────────────
    # omega_t (primary/required) and omega_h (advanced/optional) are
    # presented together under a single "McDonald's Omega" tab, each with
    # its own sub-heading — rather than as two separate top-level tabs,
    # which was found to be confusing in practice (they are two facets
    # of the same underlying construct-reliability question, not two
    # unrelated statistics).
    om_detail = res.get("omega_detail") or {}
    om_loadings = om_detail.get("loadings", np.array([]))
    om_has_detail = om_loadings is not None and len(om_loadings) > 0
    if om_has_detail:
        om_names = om_detail.get("item_names", [f"Item {i+1}" for i in range(len(om_loadings))])
        om_comm  = om_detail.get("communalities", np.array([]))
        om_err   = om_detail.get("unique_variances", np.array([]))
        omega_table2 = (["Item", "Factor Loading (\u03bb)", "Communality (\u03bb\u00b2)",
                          "Unique Variance (1\u2212\u03bb\u00b2)"],
                         [[om_names[j], _f(om_loadings[j]), _f(om_comm[j]), _f(om_err[j])]
                          for j in range(len(om_names))])
        omega_note = ("Estimated via iterated Principal Axis Factoring (PAF) \u2014 a "
                       "genuine common-factor extraction, not principal component "
                       "analysis (PCA). PCA does not partition variance into common "
                       "vs unique components and cannot be validly labelled McDonald's "
                       "omega; PAF iteratively estimates each item's communality (via "
                       "squared multiple correlation, then refines through the reduced "
                       "correlation matrix) until convergence \u2014 see Gorsuch (1983), "
                       "Factor Analysis, Ch. 5. The table above shows each item's "
                       "common-factor loading, communality (\u03bb\u00b2, proportion of "
                       "that item's variance explained by the common factor), and "
                       "unique variance (1\u2212\u03bb\u00b2, residual/error variance).")
    else:
        omega_table2 = None
        omega_note = ("Estimated via iterated Principal Axis Factoring (a genuine "
                       "common-factor extraction). Item-level decomposition requires "
                       "at least 3 items and a non-degenerate correlation matrix; not "
                       "available for this construct" +
                       (f" (only {k} item{'s' if k != 1 else ''})." if k < 3 else "."))

    omega_model_implied = om_detail.get("omega_model_implied", np.nan)
    omega_observed = om_detail.get("omega_observed", omega)  # fallback to legacy key
    omega_gap = (abs(omega_model_implied - omega_observed)
                 if (not (isinstance(omega_model_implied, float) and np.isnan(omega_model_implied))
                     and not (isinstance(omega_observed, float) and np.isnan(omega_observed)))
                 else np.nan)
    gap_note = (f" <b>Automatic note:</b> the two \u03c9u estimates differ by "
                f"{_f(omega_gap)}. Per Bentler (2009) and Kelley &amp; "
                f"Pornprasertmanit (2016), a larger gap here is itself diagnostic of "
                f"one-factor model misfit \u2014 i.e., the single-factor model does not "
                f"fully reproduce the observed inter-item correlations. Consider "
                f"examining the inter-item correlation matrix and item-level "
                f"loadings above for items that may be poorly explained by a single "
                f"common factor."
                if (not np.isnan(omega_gap) and omega_gap > 0.01) else
                (f" <b>Automatic note:</b> the two \u03c9u estimates are very close "
                 f"(gap = {_f(omega_gap)}), consistent with good one-factor model fit."
                 if not np.isnan(omega_gap) else ""))

    terminology_note = (" <b>On terminology:</b> both estimates above are the SAME "
                         "coefficient \u2014 McDonald's \u03c9u ('omega, unidimensional "
                         "model') \u2014 evaluated on two different, both-legitimate "
                         "variance bases, not two different-named coefficients. "
                         "Software and secondary sources are inconsistent here: R's "
                         "semTools::reliability() labels the model-implied-basis rows "
                         "\u2018omega\u2019/\u2018omega2\u2019 and the observed-variance-basis "
                         "row \u2018omega3\u2019; some tools and secondary sources instead "
                         "use the labels \u03c9t (\u2018omega total\u2019) and \u03c9u "
                         "interchangeably for these two bases, or mislabel the "
                         "observed-variance form \u2018omega hierarchical\u2019 \u2014 a "
                         "usage Flora (2020, footnote 7) explicitly flags as "
                         "incorrect. In this application, \u2018\u03c9 hierarchical "
                         "(\u03c9h)\u2019 is reserved exclusively for the bifactor-model "
                         "estimate below (Zinbarg et al., 2005; Rodriguez, Reise, "
                         "&amp; Haviland, 2016), never for either \u03c9u basis.")

    omega_mi_has_ci = "omega_model_implied_ci_lo" in om_detail
    _omega_mi_ci_txt = "\u2014"
    if omega_mi_has_ci:
        try:
            _omega_mi_ci_txt = _fmt_ci(om_detail.get("omega_model_implied_ci_lo", np.nan),
                                        om_detail.get("omega_model_implied_ci_hi", np.nan))
        except Exception:
            pass

    omega_mi_section = {
        "heading": "McDonald's \u03c9u \u2014 Model-Implied Variance (Primary)",
        "cards": [("McDonald's \u03c9u (model-implied)", _f(omega_model_implied),
                   alpha_label(omega_model_implied))],
        "table": (["Statistic", "Value"], [
            ["McDonald's \u03c9u (model-implied variance)", _f(omega_model_implied)],
        ] + ([["95% CI (bootstrap)", _omega_mi_ci_txt]] if omega_mi_has_ci else []) + [
            ["N of Items", str(k)],
            ["Extraction method", "Iterated Principal Axis Factoring"],
            ["Denominator basis", "(\u03a3\u03bb\u2c7c)\u00b2 + \u03a3(1\u2212\u03bb\u00b2\u2c7c)  (model-implied)"],
        ]),
        "table2": omega_table2,
        "table2_note": ("\u03bb\u2c7c estimated via iterated common-factor extraction "
                         "(PAF) on the inter-item correlation matrix; sign fixed so "
                         "\u03a3\u03bb\u2c7c \u2265 0.") if om_has_detail else "",
        "params": ("PRIMARY / headline reliability estimate for this module. "
                   "\u03c9u = (\u03a3\u03bb\u2c7c)\u00b2 / \u03c3\u0302X\u00b2, where \u03c3\u0302X\u00b2 here is the "
                   "variance IMPLIED BY the fitted one-factor model itself "
                   "[(\u03a3\u03bb\u2c7c)\u00b2 + \u03a3(1\u2212\u03bb\u00b2\u2c7c)]. Unlike Cronbach's \u03b1, "
                   "\u03c9u does not assume tau-equivalence (equal item loadings)."),
        "interp": (f"McDonald\u2019s \u03c9u (model-implied) = {_f(omega_model_implied)}, "
                   f"indicating <b>{alpha_label(omega_model_implied)}</b> reliability "
                   f"of the composite score according to the fitted congeneric "
                   f"(one-factor) measurement model. This is the recommended default "
                   f"\u03c9u estimate for standard internal-consistency reporting "
                   f"(Flora, 2020)."
                   + (f" Compared to Cronbach\u2019s alpha ({_f(a)}), \u03c9u is "
                      f"{'higher' if (omega_model_implied is not None and a is not None and not np.isnan(omega_model_implied) and not np.isnan(a) and omega_model_implied > a) else 'lower' if (omega_model_implied is not None and a is not None and not np.isnan(omega_model_implied) and not np.isnan(a) and omega_model_implied < a) else 'essentially equal'} "
                      f"by {_f(abs(omega_model_implied - a)) if (a is not None and not (isinstance(omega_model_implied,float) and np.isnan(omega_model_implied)) and not (isinstance(a,float) and np.isnan(a))) else '.'}"
                      + (f", suggesting departure from strict tau-equivalence (unequal "
                         f"common-factor loadings) \u2014 \u03c9u is the more appropriate "
                         f"estimate in that case." if (a is not None
                             and not (isinstance(omega_model_implied,float) and np.isnan(omega_model_implied))
                             and not (isinstance(a,float) and np.isnan(a))
                             and abs(omega_model_implied-a) > 0.02) else ".")
                      if (a is not None and not (isinstance(omega_model_implied,float) and np.isnan(omega_model_implied))
                      and not (isinstance(a,float) and np.isnan(a))) else "")),
        "note": (omega_note + " Purpose: estimates composite-score reliability with "
                 "respect to the target construct represented by the fitted "
                 "congeneric factor model, without assuming tau-equivalence. When "
                 "to use: as the PRIMARY, default \u03c9u estimate for standard "
                 "internal-consistency reporting (Flora, 2020, p. 488). Limitation: "
                 "assumes a single common factor (unidimensionality) and that the "
                 "one-factor model is not badly misspecified; for multidimensional "
                 "scales, see \u03c9 hierarchical below. References: Flora, D.B. "
                 "(2020). Advances in Methods and Practices in Psychological "
                 "Science, 3(4), 484\u2013501; McDonald, R.P. (1999). Test Theory: A "
                 "Unified Treatment. Erlbaum." + terminology_note),
    }

    omega_obs_has_ci = "omega_observed_ci_lo" in om_detail
    _omega_obs_ci_txt = "\u2014"
    if omega_obs_has_ci:
        try:
            _omega_obs_ci_txt = _fmt_ci(om_detail.get("omega_observed_ci_lo", np.nan),
                                         om_detail.get("omega_observed_ci_hi", np.nan))
        except Exception:
            pass

    omega_obs_section = {
        "heading": "McDonald's \u03c9u \u2014 Observed Variance (Secondary / Diagnostic)",
        "cards": [("McDonald's \u03c9u (observed)", _f(omega_observed),
                   alpha_label(omega_observed))],
        "table": (["Statistic", "Value"], [
            ["McDonald's \u03c9u (observed variance)", _f(omega_observed)],
        ] + ([["95% CI (bootstrap)", _omega_obs_ci_txt]] if omega_obs_has_ci else []) + [
            ["N of Items", str(k)],
            ["Denominator basis", "sample/observed Var(X)"],
            ["Gap vs. model-implied \u03c9u", _f(omega_gap)],
        ]),
        "params": ("SECONDARY / DIAGNOSTIC estimate. \u03c9u = (\u03a3\u03bb\u2c7c)\u00b2 / \u03c3\u0302X\u00b2, "
                   "where \u03c3\u0302X\u00b2 here is the ACTUAL observed sample variance of "
                   "the total score, independent of how well the one-factor model "
                   "fits the data."),
        "interp": (f"McDonald\u2019s \u03c9u (observed variance) = {_f(omega_observed)}: "
                   f"the proportion of the ACTUAL, empirically observed total-score "
                   f"variance attributable to the specified common factor."),
        "note": ("Purpose: relates model-based common-factor variance directly to "
                 "the actually observed composite-score variance, rather than to "
                 "the model's own implied variance. When to use: as a secondary "
                 "diagnostic specifically when the researcher wants this "
                 "model-to-observed comparison, or per Kelley & Pornprasertmanit "
                 "(2016), who found confidence-interval coverage for \u03c9u tends to "
                 "be better when the observed sample variance is used as the "
                 "denominator. This is NOT automatically the preferred estimate "
                 "over the model-implied form above \u2014 both are legitimate; the "
                 "gap between them (reported above) is itself informative. "
                 "Reference: Kelley, K., & Pornprasertmanit, S. (2016). "
                 "Psychological Methods, 21(1), 69\u201392." + gap_note),
    }

    omh_computable = omh.get("computable", False)
    omh_value = omh.get("omega_h", np.nan)
    if omh_computable:
        omh_general = omh.get("general_loadings", np.array([]))
        omh_specific = omh.get("specific_loadings", np.array([]))
        omh_names = omh.get("item_names", [f"Item {i+1}" for i in range(len(omh_general))])
        omh_t_bifactor = omh.get("omega_t_bifactor", np.nan)
        omh_table = (["Statistic", "Value"], [
            ["McDonald's Omega Hierarchical (\u03c9h)", _f(omh_value)],
            ["95% CI (bootstrap)", "Not computed \u2014 see note below"],
            ["N of Items", str(k)],
            ["Group factors extracted", str(omh.get("n_factors_used", "\u2014"))],
            ["\u03c9 total within this bifactor model", _f(omh_t_bifactor)],
        ])
        # Specific/group-factor loadings (Schmid-Leiman matrix S) were
        # previously computed by the engine but discarded before reaching
        # the UI. Surfaced here as additional columns alongside the
        # general-factor loading, so a user can see each item's full
        # bifactor decomposition (general + every specific factor), not
        # only its general-factor component.
        n_specific = omh_specific.shape[1] if (hasattr(omh_specific, "shape") and omh_specific.ndim == 2) else 0
        omh_table2_header = ["Item", "General-Factor Loading"] + [
            f"Specific Factor {j+1} Loading" for j in range(n_specific)]
        omh_table2_rows = []
        for i in range(len(omh_names)):
            row = [omh_names[i], _f(omh_general[i])]
            for j in range(n_specific):
                row.append(_f(omh_specific[i, j]))
            omh_table2_rows.append(row)
        omh_table2 = (omh_table2_header, omh_table2_rows)
        ratio = (omh_value/omh_t_bifactor) if (omh_t_bifactor and omh_t_bifactor > 1e-9) else np.nan
        omh_interp = (f"McDonald\u2019s \u03c9h = {_f(omh_value)}: an estimated "
                      f"{_f(ratio*100 if not np.isnan(ratio) else np.nan)}% of this "
                      f"construct's total common variance is attributable specifically "
                      f"to the single general factor shared by all items, with the "
                      f"remainder attributable to {omh.get('n_factors_used')} "
                      f"group-specific factor(s). {omh.get('reason','')}")
        omh_note = ("\u03c9h answers a DIFFERENT question than \u03c9t: \u03c9t asks "
                    "\u2018how much total variance is systematic at all\u2019 (general + "
                    "group-specific combined); \u03c9h asks \u2018how much reflects "
                    "the single construct common to every item\u2019 (general only). "
                    "\u03c9h \u2264 \u03c9t always. \u03c9h should NOT automatically "
                    "replace \u03c9t as the headline statistic \u2014 most scales are "
                    "adequately summarised by \u03c9t alone; \u03c9h is specifically "
                    "informative when a scale is knowingly multidimensional and the "
                    "question is how much reliability survives after separating out "
                    "the general construct from its sub-facets. Method: "
                    f"{omh.get('n_factors_used')}-factor oblique Principal Axis "
                    "Factoring (direct oblimin rotation) followed by the Schmid-Leiman "
                    "bifactor transformation. References: Schmid, J. & Leiman, J.M. "
                    "(1957). Psychometrika, 22(1), 53\u201361; Zinbarg, R.E., Revelle, "
                    "W., Yovel, I., & Li, W. (2005). Psychometrika, 70(1), 123\u2013133; "
                    "McDonald, R.P. (1999). Test Theory: A Unified Treatment.<br/><br/>"
                    "<b>Why no confidence interval:</b> " +
                    omh.get("omega_h_ci_reason",
                            "A bootstrap confidence interval is not computed for "
                            "omega-hierarchical, since its oblique-rotation extraction "
                            "was found to take substantial, unpredictable time for "
                            "certain data structures, independent of item count."))
        omega_h_section = {
            "heading": "McDonald's Omega Hierarchical (\u03c9h) \u2014 Advanced / Optional",
            "cards": [("McDonald's \u03c9h", _f(omh_value),
                       f"{_f(ratio*100 if not np.isnan(ratio) else np.nan)}% general-factor")],
            "table": omh_table,
            "table2": omh_table2,
            "table2_note": ("General-factor loading and specific/group-factor loading(s) "
                             "per item, after Schmid-Leiman orthogonalisation (general and "
                             "specific factors are mutually uncorrelated by construction). "
                             "A high specific-factor loading alongside a low general-factor "
                             "loading indicates that item is driven mainly by its group-"
                             "specific facet rather than the construct common to all items."),
            "params": ("ADVANCED / OPTIONAL. Requires a genuine bifactor (general + "
                       "group-factor) structure; see note for gating criteria and "
                       "why this was computable for this construct."),
            "interp": omh_interp,
            "note": omh_note,
        }
    else:
        omh_reason = omh.get("reason", "Omega hierarchical was not computed for this construct.")
        omega_h_section = {
            "heading": "McDonald's Omega Hierarchical (\u03c9h) \u2014 Advanced / Optional",
            "cards": [("McDonald's \u03c9h", "N/A", "Not computable")],
            "table": (["Statistic", "Value"],
                      [["Status", "Not computed"], ["Reason", omh_reason]]),
            "params": ("ADVANCED / OPTIONAL. \u03c9h requires a genuine bifactor "
                       "(general + \u22652 group-factor) structure: at least 6 items, "
                       "and at least 2 eigenvalues of the inter-item correlation "
                       "matrix exceeding 1.0 (Kaiser criterion)."),
            "interp": (f"<b>\u03c9 hierarchical was not computed for this construct.</b> "
                       f"{omh_reason} This is an intentional methodological safeguard, "
                       f"<b>not a computation error</b> \u2014 forcing a bifactor "
                       f"estimate on data that do not support one would produce an "
                       f"unstable, misleading number. \u03c9t (above) remains the "
                       f"valid, primary reliability estimate for this construct."),
            "note": ("\u03c9h answers a narrower question than \u03c9t (reliability "
                     "attributable to a single general factor specifically, as "
                     "distinct from all common variance combined) and is only "
                     "meaningful for scales with a genuine multi-facet structure. "
                     "References: Schmid, J. & Leiman, J.M. (1957). Psychometrika, "
                     "22(1), 53\u201361; McDonald, R.P. (1999). Test Theory: A Unified "
                     "Treatment."),
        }

    blocks.append({
        "key": "Omega", "title": "McDonald's Omega",
        "sections": [omega_mi_section, omega_obs_section, omega_h_section],
        # Top-level fields kept minimal/unused when "sections" is present;
        # required keys still populated defensively for any legacy caller.
        "cards": [], "table": None, "interp": "", "params": "", "note": "",
    })

    # ── Guttman's Lambda: dual-basis (raw covariance + standardized) ──────
    # These are NOT two different theories: same Guttman (1945) lambda
    # family, computed on two legitimate but different measurement bases.
    lam_raw = lam.get("raw", lam)          # backward-compat fallback
    lam_std = lam.get("standardized", {})

    def _lambda_rows_with_ci(lam_basis):
        """Builds Guttman-lambda rows, adding a 95% CI column only when
        bootstrap CI data is actually present (compute_bootstrap_ci was
        requested) -- avoids a column of blank dashes when the user has
        not opted in."""
        _has_ci = any(f"lambda{i}_ci_lo" in lam_basis for i in range(1, 7))
        rows = []
        for i in range(1, 7):
            row = [f"Guttman \u03bb{i}", _f(lam_basis.get(f'lambda{i}'))]
            if _has_ci:
                _lo = lam_basis.get(f"lambda{i}_ci_lo", np.nan)
                _hi = lam_basis.get(f"lambda{i}_ci_hi", np.nan)
                _method = lam_basis.get(f"lambda{i}_ci_method", "")
                try:
                    _ci_txt = _fmt_ci(_lo, _hi)
                except Exception:
                    _ci_txt = "\u2014"
                row.append(_ci_txt)
            rows.append(row)
        return rows, _has_ci

    lam_raw_rows, _lam_raw_has_ci = _lambda_rows_with_ci(lam_raw)
    lam_std_rows, _lam_std_has_ci = _lambda_rows_with_ci(lam_std)
    l2r, l3r = lam_raw.get("lambda2"), lam_raw.get("lambda3")
    l4_method = lam_raw.get("lambda4_method", "n/a")
    l4_n_splits = lam_raw.get("lambda4_n_splits", 0)
    l4_method_txt = ({
        "exhaustive": f"true maximum \u2014 exhaustively searched across all "
                      f"{l4_n_splits} distinct non-trivial splits",
        "sampled": (f"best value found among {l4_n_splits:,} randomly sampled "
                    f"non-trivial splits (item count exceeds the exhaustive-search "
                    f"threshold of 16 items) \u2014 not the guaranteed true maximum, "
                    f"but a close estimate; methodology follows Revelle, W. psych "
                    f"package's splitHalf() function, which switches from exhaustive "
                    f"search to random sampling at the same item-count threshold"),
        "n/a": "not computed",
    }).get(l4_method, l4_method)

    # Automatic recommendation: raw vs standardized basis divergence
    # signals item-scale heterogeneity (large SD differences across items).
    l3_std_val = lam_std.get("lambda3")
    basis_gap = (abs(l3r - l3_std_val)
                 if (l3r is not None and l3_std_val is not None
                     and not (isinstance(l3r, float) and np.isnan(l3r))
                     and not (isinstance(l3_std_val, float) and np.isnan(l3_std_val)))
                 else np.nan)
    basis_recommendation = (
        f" <b>Automatic note:</b> raw-basis \u03bb\u2083 ({_f(l3r)}) and "
        f"standardized-basis \u03bb\u2083 ({_f(l3_std_val)}) differ by {_f(basis_gap)} "
        f"\u2014 a gap this size typically indicates items have substantially "
        f"different standard deviations (scale heterogeneity). Consider whether "
        f"raw or standardized combination is more substantively appropriate for "
        f"this scale."
        if (not np.isnan(basis_gap) and basis_gap > 0.02) else "")

    # Automatic recommendation: dimensionality signal via Kaiser eigenvalue
    # criterion (validated via Monte Carlo simulation to correctly identify
    # unidimensional vs multi-factor data in ~80-100% of cases — a simpler
    # "lambda4 minus mean of other lambdas" gap heuristic was tested first
    # and found NOT to discriminate reliably, so it was not used).
    n_eig = lam_raw.get("n_eigenvalues_above_1")
    dimensionality_note = ""
    if n_eig is not None and n_eig >= 2:
        dimensionality_note = (
            f" <b>Automatic note:</b> {n_eig} eigenvalues of the inter-item "
            f"correlation matrix exceed 1.0 (Kaiser, 1960 criterion), suggesting "
            f"this construct may not be strictly unidimensional. If McDonald's "
            f"\u03c9 hierarchical is reported above as computable, its value "
            f"reflects this structure directly; otherwise, consider a dedicated "
            f"exploratory factor analysis to examine potential sub-facets before "
            f"treating this scale as measuring a single construct.")

    lambda_raw_section = {
        "heading": "Raw Covariance Basis",
        "cards": [("\u03bb2 (raw)", _f(l2r), alpha_label(l2r)),
                  ("\u03bb3 = \u03b1 (raw)", _f(l3r), alpha_label(l3r))],
        "table": (["Coefficient", "Value", "95% CI (bootstrap)"] if _lam_raw_has_ci
                  else ["Coefficient", "Value"], lam_raw_rows),
        "params": ("Computed from the item COVARIANCE matrix (original item scales "
                   "preserved). \u03bb\u2083 equals raw-score Cronbach's alpha. \u03bb\u2084 "
                   f"method: {l4_method_txt}."),
        "interp": (f"Guttman\u2019s \u03bb\u2082 (raw) = {_f(l2r)} (<b>{alpha_label(l2r)}</b>); "
                   f"\u03bb\u2083 (raw) = {_f(l3r)}, equal to Cronbach\u2019s alpha computed on "
                   f"the original item scales." + basis_recommendation + dimensionality_note),
        "note": ("\u03bb\u2081: weakest lower bound (Guttman, 1945, Eq. 1). \u03bb\u2082: "
                 "improves on \u03bb\u2081 using covariance structure (Eq. 2). \u03bb\u2083: "
                 "= Cronbach's \u03b1 (Eq. 3). \u03bb\u2084: true maximum split-half "
                 "reliability via exhaustive search over all non-trivial splits "
                 "(Eq. 4) \u2014 the tightest split-half-type bound. \u03bb\u2085: uses the "
                 "largest column-sum of squared covariances (Eq. 5). \u03bb\u2086: uses "
                 "squared multiple correlations (SMC) to isolate unique variance "
                 "(Eq. 6); requires an invertible correlation matrix, may be "
                 "undefined for collinear items. Proven ordering \u03bb\u2081 \u2264 \u03bb\u2083 "
                 "\u2264 \u03bb\u2082 holds when \u03bb\u2081 \u2265 0 (Guttman, 1945); no universal "
                 "ordering is proven among \u03bb\u2084, \u03bb\u2085, \u03bb\u2086 \u2014 their relative "
                 "size depends on the specific covariance structure. Reference: "
                 "Guttman, L. (1945). A basis for analyzing test-retest reliability. "
                 "Psychometrika, 10(4), 255\u2013282."
                 + (" 95% confidence intervals are percentile-bootstrap, following "
                    "the method recommended for reliability coefficients by Kelley, "
                    "K., &amp; Pornprasertmanit, S. (2016). Psychological Methods, "
                    "21(1), 69\u201392." if _lam_raw_has_ci else "")),
    }

    l2s = lam_std.get("lambda2")
    lambda_std_section = {
        "heading": "Standardized Correlation Basis",
        "cards": [("\u03bb2 (standardized)", _f(l2s), alpha_label(l2s)),
                  ("\u03bb3 = \u03b1 (standardized)", _f(l3_std_val), alpha_label(l3_std_val))],
        "table": (["Coefficient", "Value", "95% CI (bootstrap)"] if _lam_std_has_ci
                  else ["Coefficient", "Value"], lam_std_rows),
        "params": ("Same Guttman (1945) lambda family as above (see Raw Covariance "
                   "Basis section), computed on the item CORRELATION matrix instead "
                   "(each item implicitly rescaled to unit variance before "
                   "combination). \u03bb\u2083 here equals STANDARDIZED Cronbach's alpha."),
        "interp": (f"Guttman\u2019s \u03bb\u2082 (standardized) = {_f(l2s)} "
                   f"(<b>{alpha_label(l2s)}</b>); \u03bb\u2083 (standardized) = "
                   f"{_f(l3_std_val)}."),
        "note": ("Use this basis when items are measured on different scales and "
                 "should be equalised (unit variance) before combination. The raw "
                 "basis (above) is preferable when the original item-scale "
                 "differences are themselves substantively meaningful. Neither "
                 "basis is universally \u2018more correct\u2019 \u2014 the appropriate "
                 "choice depends on measurement context, not on which number is "
                 "larger. Reference: Guttman, L. (1945). Psychometrika, 10(4), "
                 "255\u2013282."
                 + (" 95% confidence intervals are percentile-bootstrap (Kelley &amp; "
                    "Pornprasertmanit, 2016)." if _lam_std_has_ci else "")),
    }

    blocks.append({
        "key": "Lambda", "title": "Guttman's Lambda",
        "sections": [lambda_raw_section, lambda_std_section],
        "cards": [], "table": None, "interp": "", "params": "", "note": "",
    })

    if sh.get("error"):
        # k < 4: Spearman-Brown requires equal-length halves, which is not
        # meaningful below 4 items (a 3-item split gives 1 item vs 2 items).
        # Render an explicit, visible rejection message instead of silently
        # falling through to a table of "." placeholders with no explanation
        # — an empty-looking table with no message reads as a software error
        # to users, when it is in fact a deliberate, documented minimum.
        _n_items_sh = sh.get("n_items", k)
        blocks.append({
            "key": "Split-half", "title": "Split-Half",
            "cards": [("Split-Half", "N/A", "Requires \u2265 4 items")],
            "table": (["Statistic", "Value"],
                      [["Status", "Not computed"],
                       ["Reason", sh.get("message", "Split-half analysis requires at least 4 items.")],
                       ["N of Items (this construct)", str(_n_items_sh)],
                       ["Minimum Required", "4"]]),
            "params": ("Spearman-Brown assumes equal-length, equally-reliable "
                       "halves; with fewer than 4 items a first/second split "
                       "cannot produce two halves of comparable length "
                       "(e.g. 3 items \u2192 1 item vs 2 items), so the "
                       "correction is not meaningful."),
            "interp": (f"<b>Split-half reliability was not computed for this "
                       f"construct.</b> It contains {_n_items_sh} item"
                       f"{'s' if _n_items_sh != 1 else ''}, below the minimum "
                       f"of 4 required for a meaningful equal-length split. "
                       f"This is an intentional methodological safeguard, "
                       f"<b>not a computation error</b> \u2014 no split-half "
                       f"value can be validly reported for scales this short."),
            "note": ("To obtain split-half reliability for this construct, "
                     "include at least 4 items. Cronbach's alpha, McDonald's "
                     "omega, and Guttman's lambda coefficients remain valid "
                     "and are reported above regardless of item count."),
        })
    else:
        sb = sh.get("spearman_brown"); gut = sh.get("guttman"); rh = sh.get("r_halves")
        a1 = sh.get("alpha_part1"); a2 = sh.get("alpha_part2")
        n1 = sh.get("n_part1", ""); n2 = sh.get("n_part2", "")
        ntot = (int(n1) + int(n2)) if (str(n1).isdigit() and str(n2).isdigit()) else ""

        # Supplementary variants (additive — the first-second half result
        # above remains PRIMARY and unchanged; these are shown alongside,
        # not in place of it, per spec).
        oe = sh.get("odd_even", {})
        mx = sh.get("maximum", {})
        fsh = sh.get("first_second", {})
        mx_method = mx.get("method", "n/a")
        mx_n = mx.get("n_splits_evaluated", 0)
        mx_method_label = {
            "exhaustive": f"exhaustive, n={mx_n:,}",
            "sampled": f"sampled, n={mx_n:,}",
            "n/a": "n/a",
        }.get(mx_method, mx_method)
        _sh_has_ci = "spearman_brown_ci_lo" in fsh
        variants_table2 = None
        variants_note = ""
        if oe or mx:
            if _sh_has_ci:
                def _ci_cell(d, key):
                    try:
                        return _fmt_ci(d.get(f"{key}_ci_lo", np.nan), d.get(f"{key}_ci_hi", np.nan))
                    except Exception:
                        return "\u2014"
                variants_table2 = (
                    ["Split Method", "r", "Spearman-Brown", "SB 95% CI",
                     "Guttman SH", "Guttman 95% CI"],
                    [["First-Second Half (primary, above)", _f(rh), _f(sb),
                      _ci_cell(fsh, "spearman_brown"), _f(gut), _ci_cell(fsh, "guttman")],
                     ["Odd-Even Split", _f(oe.get("r_halves")), _f(oe.get("spearman_brown")),
                      _ci_cell(oe, "spearman_brown"), _f(oe.get("guttman")), _ci_cell(oe, "guttman")],
                     [f"Maximum Split-Half ({mx_method_label})",
                      _f(mx.get("r_halves")), _f(mx.get("spearman_brown")),
                      _ci_cell(mx, "spearman_brown"), _f(mx.get("guttman")),
                      "\u2014 (Guttman-SH not separately optimized for this variant)"]])
            else:
                variants_table2 = (
                    ["Split Method", "r (between halves)", "Spearman-Brown", "Guttman Split-Half"],
                    [["First-Second Half (primary, above)", _f(rh), _f(sb), _f(gut)],
                     ["Odd-Even Split", _f(oe.get("r_halves")), _f(oe.get("spearman_brown")),
                      _f(oe.get("guttman"))],
                     [f"Maximum Split-Half ({mx_method_label})",
                      _f(mx.get("r_halves")), _f(mx.get("spearman_brown")), _f(mx.get("guttman"))]])
            variants_note = (
                "Odd-even split (items at odd vs even positions) is the classical "
                "alternative to the first-second-half convention shown above. "
                "Maximum split-half is found via its own search (exhaustive for "
                "\u226416 items; for larger scales, "
                f"{mx_n:,} randomly sampled non-trivial partitions, following the "
                "same threshold and methodology as R's psych::splitHalf() -- "
                "Revelle, W. psych package documentation and NEWS) specifically "
                "maximising the Spearman-Brown coefficient. "
                "<b>Important:</b> this search target is deliberately independent "
                "from Guttman's \u03bb\u2084 (see Guttman's Lambda section), which "
                "maximises a different criterion (the variance-ratio formula). "
                "When item variances are heterogeneous, the split that maximises "
                "\u03bb\u2084 is not always the same split that maximises "
                "Spearman-Brown \u2014 the two are related but distinct "
                "optimisation targets, so this module reports each against its "
                "own correct maximum rather than reusing one for the other. "
                "All three split-half variants are legitimate; they will "
                "generally differ, and no single one is the definitive "
                "\u2018true\u2019 split-half estimate. The first-second-half result "
                "above remains the primary, headline split-half statistic for "
                "this module."
            )

        blocks.append({
            "key": "Split-half", "title": "Split-Half",
            "cards": [("Spearman-Brown", _f(sb), alpha_label(sb)),
                      ("Guttman split-half", _f(gut), alpha_label(gut))],
            "table": (["Statistic", "Part 1", "Part 2", "Overall"],
                      [["Cronbach's Alpha", _f(a1), _f(a2), ""],
                       ["N of Items", str(n1), str(n2), str(ntot)],
                       ["Correlation Between Forms", "", "", _f(rh)],
                       ["Spearman-Brown Coefficient", "", "", _f(sb)],
                       ["Guttman Split-Half Coefficient", "", "", _f(gut)]]),
            "table2": variants_table2,
            "table2_note": variants_note,
            "params": ("PRIMARY result: items split into first vs second half. "
                       "Spearman-Brown assumes equal-length, equally-reliable "
                       "halves. Supplementary split methods (odd-even, maximum) "
                       "are tabulated below for comparison."),
            "interp": (f"The Spearman-Brown split-half coefficient = {_f(sb)} "
                       f"(<b>{alpha_label(sb)}</b>); the Guttman split-half = {_f(gut)}. "
                       f"The two halves correlate r = {_f(rh)}."),
            "note": ("A low or negative split-half value alongside an adequate omega "
                     "often signals a reverse-scored item or multidimensionality. "
                     "References: Spearman, C. (1910); Brown, W. (1910); Guttman, L. "
                     "(1945). Psychometrika, 10(4), 255\u2013282."),
        })

    if dich:
        _kr_oor  = (kr is not None and not (isinstance(kr, float) and np.isnan(kr))
                    and kr > 1)
        _item_p  = res.get("item_p",  np.array([]))
        _item_pq = res.get("item_pq", np.array([]))
        # Fallback: compute item_p from item_stats if engine was old version
        if len(_item_p) == 0 and "item_stats" in res:
            _ist = res["item_stats"]
            if _ist is not None and not _ist.empty and "Mean" in _ist.columns:
                _item_p  = _ist["Mean"].values
                _item_pq = _item_p * (1 - _item_p)
        _item_names = res.get("item_names",
                              [f"Item {i+1}" for i in range(len(_item_p))])
        # Item-level diagnostic table
        _item_rows = [["Item", "p (proportion correct)",
                       "p\u00d7q (item variance)", "Diagnosis"]]
        for _i, (_pv, _pqv) in enumerate(zip(_item_p, _item_pq)):
            _nm = _item_names[_i] if _i < len(_item_names) else f"Item {_i+1}"
            if float(_pv) < 0.1 or float(_pv) > 0.9:
                _dx = "\u26a0\ufe0f Near-zero variance (p extreme)"
            elif float(_pqv) < 0.05:
                _dx = "\u26a0\ufe0f Very low item variance"
            else:
                _dx = "\u2713 OK"
            _item_rows.append([_nm, _f(float(_pv)), _f(float(_pqv)), _dx])
        _has_diag = len(_item_rows) > 1  # more than just header

        # KR-20 table: two rows when out-of-range (original + capped for appendix)
        _kr_capped = min(float(kr), 1.0) if (kr is not None and not
                        (isinstance(kr, float) and np.isnan(kr))) else np.nan
        _kr21_val = res.get("kr21", np.nan)
        _astd_val = res.get("alpha_std", np.nan)
        _sem_val = res.get("sem", np.nan)
        _sem_basis = res.get("sem_basis", "KR-20")
        _sstats = res.get("scale_stats", {})

        # ── Section 1: Reliability Coefficients ─────────────────────────
        if _kr_oor:
            _rel_rows = [["KR-20 (calculated)", _f(kr)],
                         ["KR-20 (adjusted for report, capped at 1.000)", _f(_kr_capped)],
                         ["KR-21", _f(_kr21_val)],
                         ["Standardized Alpha (correlation-basis)", _f(_astd_val)],
                         ["N of Items", str(k)]]
            _rel_note = (
                "<b>\u26a0\ufe0f KR-20 = " + _f(kr) + " \u2014 out-of-range (value &gt; 1).</b> "
                "This is <b>not a calculation error</b>; it is a known, "
                "well-documented mathematical property reproduced identically "
                "by any correct implementation of the formula. It occurs "
                "when one or more items have near-zero variance (p \u2248 0 or "
                "p \u2248 1). Use the adjusted value (1.000) in report appendices, "
                "with a methodological note explaining the extreme item "
                "difficulty. See Item-Level Diagnostics below for which "
                "items are responsible.")
            _card_lbl = "\u26a0\ufe0f Out-of-range (> 1)"
        else:
            _rel_rows = [["KR-20", _f(kr)],
                         ["KR-21", _f(_kr21_val)],
                         ["Standardized Alpha (correlation-basis)", _f(_astd_val)],
                         ["N of Items", str(k)]]
            _rel_note = ""
            _card_lbl = alpha_label(kr)

        _gap_kr20_kr21 = (abs(kr - _kr21_val)
                          if (not (isinstance(kr, float) and np.isnan(kr))
                              and not (isinstance(_kr21_val, float) and np.isnan(_kr21_val)))
                          else np.nan)
        reliability_section = {
            "heading": "Reliability Coefficients",
            "cards": [("KR-20", _f(_kr_capped if _kr_oor else kr), _card_lbl),
                      ("KR-21", _f(_kr21_val), alpha_label(_kr21_val)),
                      ("Standardized \u03b1", _f(_astd_val), alpha_label(_astd_val))],
            "table": (["Statistic", "Value"], _rel_rows),
            "params": (
                "KR-20 applies to dichotomous (0/1) items and equals "
                "Cronbach\u2019s alpha exactly for binary data (Kuder & "
                "Richardson, 1937). KR-21 is a simplified, more conservative "
                "form assuming equal item difficulty (KR-21 \u2264 KR-20 always). "
                "Standardized Alpha uses the correlation (not covariance) "
                "basis \u2014 for genuinely dichotomous 0/1 items this will "
                "generally differ from KR-20/raw-\u03b1 since item variances "
                "p\u00b7q differ across items even when all are dichotomous."),
            "interp": ((f"KR-20 = {_f(kr)}, indicating <b>{alpha_label(kr)}</b> "
                       f"internal consistency for these dichotomous items."
                       + (f" KR-21 = {_f(_kr21_val)} (gap to KR-20 = {_f(_gap_kr20_kr21)}), "
                          f"the more conservative equal-difficulty approximation."
                          if not np.isnan(_gap_kr20_kr21) else "")) if not _kr_oor else
                       f"<b>\u26a0\ufe0f KR-20 = {_f(kr)} \u2014 out-of-range (value &gt; 1).</b> "
                       f"This is <b>not a calculation error</b>; it is a known, "
                       f"well-documented mathematical property reproduced "
                       f"identically by any correct implementation of the "
                       f"formula, occurring when one or more items have "
                       f"near-zero variance. Use the <b>adjusted value "
                       f"({_f(_kr_capped)})</b> in your report, indicating "
                       f"<b>{alpha_label(_kr_capped)}</b> internal consistency."
                       + (f" KR-21 = {_f(_kr21_val)}, the more conservative "
                          f"equal-difficulty approximation."
                          if not np.isnan(_kr21_val) and not (isinstance(_kr21_val,float) and np.isnan(_kr21_val)) else "")),
            "note": ("Reported because all items in this construct are "
                     "dichotomous. References: Kuder, G.F., & Richardson, "
                     "M.W. (1937). Psychometrika, 2(3), 151\u2013160." + _rel_note),
        }

        # ── Section 2: Scale-Level Statistics ────────────────────────────
        scale_section = {
            "heading": "Scale-Level Statistics",
            "cards": [("Mean (total score)", _f(_sstats.get("mean", np.nan)), ""),
                      ("SD (total score)", _f(_sstats.get("sd", np.nan)), ""),
                      ("SEM", _f(_sem_val), f"basis: {_sem_basis}")],
            "table": (["Statistic", "Value"], [
                ["Mean (total score)", _f(_sstats.get("mean", np.nan))],
                ["Median (total score)", _f(_sstats.get("median", np.nan))],
                ["SD (total score)", _f(_sstats.get("sd", np.nan))],
                ["Variance (total score)", _f(_sstats.get("variance", np.nan))],
                ["Min / Max", f"{_f(_sstats.get('min', np.nan))} / {_f(_sstats.get('max', np.nan))}"],
                ["Standard Error of Measurement (SEM)", _f(_sem_val)],
            ]),
            "params": (f"SEM = SD_total \u00d7 \u221a(1 \u2212 reliability), using "
                      f"{_sem_basis} as the reliability estimate for this "
                      f"dichotomous-item construct (Lord & Novick, 1968)."),
            "interp": (f"The observed total-score mean is {_f(_sstats.get('mean', np.nan))} "
                      f"(SD = {_f(_sstats.get('sd', np.nan))}). The Standard Error of "
                      f"Measurement is {_f(_sem_val)}, meaning an individual "
                      f"respondent\u2019s true score is expected to fall within "
                      f"approximately \u00b1{_f(1.96*_sem_val) if not np.isnan(_sem_val) else '\u2014'} "
                      f"of their observed score, 95% of the time, under classical "
                      f"test theory."),
            "note": ("SEM is useful for constructing approximate confidence "
                     "bands around an individual respondent\u2019s observed score "
                     "\u2014 distinct from the reliability coefficients above, "
                     "which describe the scale\u2019s overall consistency rather "
                     "than uncertainty around any one person\u2019s score. "
                     "Reference: Lord, F.M., & Novick, M.R. (1968). Statistical "
                     "Theories of Mental Test Scores. Addison-Wesley."),
        }

        # ── Section 3: Item-Level Diagnostics (consolidated) ─────────────
        _istats_df = res.get("item_stats")
        _item_total_r_map = {}
        _kr20_del_map = {}
        if _istats_df is not None and not _istats_df.empty:
            for _, _row in _istats_df.iterrows():
                _item_total_r_map[_row["Item"]] = _row.get("Corrected Item-Total Correlation", np.nan)
                _kr20_del_map[_row["Item"]] = _row.get("Cronbach's Alpha if Item Deleted", np.nan)

        _pq_raw_arr = res.get("item_pq_raw", np.array([]))
        _pq_sample_arr = res.get("item_pq_sample", np.array([]))
        if _istats_df is not None and not _istats_df.empty and "Item" in _istats_df.columns:
            _item_names_kr = list(_istats_df["Item"])
        else:
            _item_names_kr = [f"Item {i+1}" for i in range(len(_item_p))]

        _diag_rows = [["Item", "p (proportion)", "p\u00d7q (raw)",
                       "p\u00d7q (sample-corrected)", "Item-Total r",
                       "KR-20 if Deleted", "Diagnosis"]]
        for _i in range(len(_item_p)):
            _nm = _item_names_kr[_i] if _i < len(_item_names_kr) else f"Item {_i+1}"
            _pv = float(_item_p[_i])
            _pqr = float(_pq_raw_arr[_i]) if _i < len(_pq_raw_arr) else np.nan
            _pqs = float(_pq_sample_arr[_i]) if _i < len(_pq_sample_arr) else np.nan
            _itr = _item_total_r_map.get(_nm, np.nan)
            _kdel = _kr20_del_map.get(_nm, np.nan)
            if _pv < 0.1 or _pv > 0.9:
                _dx = "\u26a0\ufe0f Near-zero variance (p extreme)"
            elif _pqs < 0.05:
                _dx = "\u26a0\ufe0f Very low item variance"
            elif not np.isnan(_itr) and _itr < 0.1:
                _dx = "\u26a0\ufe0f Weak item-total correlation"
            else:
                _dx = "\u2713 OK"
            _diag_rows.append([_nm, _f(_pv), _f(_pqr), _f(_pqs),
                               _f(_itr), _f(_kdel), _dx])
        # Summary rows: Sum and Mean item difficulty
        _diag_rows.append(["Sum", "\u2014", _f(np.sum(_pq_raw_arr)) if len(_pq_raw_arr) else "\u2014",
                           _f(np.sum(_pq_sample_arr)) if len(_pq_sample_arr) else "\u2014",
                           "\u2014", "\u2014", ""])
        _diag_rows.append(["Mean item difficulty", _f(np.mean(_item_p)) if len(_item_p) else "\u2014",
                           "\u2014", "\u2014", "\u2014", "\u2014", ""])

        diagnostics_section = {
            "heading": "Item-Level Diagnostics",
            "table": (_diag_rows[0], _diag_rows[1:]),
            "table_left": {0, 6},
            "params": ("p\u00d7q (raw) is the population-style item variance "
                      "p(1\u2212p) \u2014 the conventional textbook quantity. "
                      "p\u00d7q (sample-corrected) = p(1\u2212p)\u00b7n/(n\u22121) is the "
                      "value that actually enters the KR-20 formula\u2019s "
                      "numerator sum. Both are shown because the two "
                      "conventions differ systematically by exactly the factor "
                      "n/(n\u22121), and different reference tools may display "
                      "either one \u2014 showing both allows direct reconciliation "
                      "without implying either alone is incorrect."),
            "interp": ("Items flagged \u26a0\ufe0f above warrant review: extreme p "
                      "(&lt;.10 or &gt;.90) indicates near-unanimous responses "
                      "and contributes little discriminating variance; weak "
                      "item-total correlation (&lt;.10) suggests the item may "
                      "not measure the same construct as the rest of the scale. "
                      "KR-20-if-deleted values above the scale\u2019s overall "
                      "KR-20 indicate removing that item would improve "
                      "reliability."),
            "note": ("KR-20-if-Deleted is numerically identical to Cronbach\u2019s "
                     "alpha-if-deleted for these dichotomous items (the two "
                     "coefficients are algebraically identical; see Kuder & "
                     "Richardson, 1937), recomputed here on the (k\u22121)-item "
                     "reduced scale for each item in turn."),
        }

        blocks.append({
            "key":        "KR-20",
            "title":      "Kuder-Richardson 20",
            "sections": [reliability_section, scale_section, diagnostics_section],
            "cards": [], "table": None, "interp": "", "params": "", "note": "",
        })
    else:
        blocks.append({
            "key": "KR-20", "title": "Kuder-Richardson 20",
            "cards": [("KR-20", "\u2014", "not applicable")],
            "table": None,
            "item_diag": None,
            "params": "KR-20 is defined only for dichotomous (0/1) items.",
            "interp": ("KR-20 is not applicable here because the items are not "
                       "dichotomous. Use Cronbach\u2019s alpha instead."),
            "note": "",
        })

    icc = res.get("icc")
    if icc is None:
        blocks.append({
            "key": "ICC", "title": "Intraclass Correlation Coefficient",
            "cards": [("ICC", "\u2014", "not computable")],
            "table": None,
            "item_diag": None,
            "params": ("ICC requires variance in both subjects and items. "
                       "It cannot be computed when all items or all persons "
                       "have identical scores (zero variance)."),
            "interp": ("\u2139\ufe0f ICC could not be computed for this construct. "
                       "This typically occurs when item scores are extremely "
                       "homogeneous \u2014 e.g., all respondents answered "
                       "identically, or all items have the same value for every "
                       "respondent. Ensure there is sufficient variability in the "
                       "data before re-running."),
            "note": ("ICC is based on a one-way or two-way random/mixed effects "
                     "model. Computed via pingouin; requires non-degenerate data "
                     "(both between-subject and within-subject variance > 0)."),
        })
    if icc is not None and not icc.empty:
        cols = list(icc.columns)
        def _icc_row_cell(v):
            # pingouin's CI95% column returns a numpy.ndarray, NOT a
            # Python list -- confirmed via direct inspection (type(v) is
            # numpy.ndarray). An isinstance(v, list) check alone misses
            # this, silently falling through to str(v) and producing
            # numpy's raw repr (e.g. "[-0.05  0.03]", double-spaced, no
            # comma, 3dp) instead of the intended 5dp bracket format.
            if isinstance(v, (list, np.ndarray)) and len(v) == 2:
                return _fmt_ci(v[0], v[1])
            if isinstance(v, (list, np.ndarray)):
                return str(v)
            if isinstance(v, (int, float, np.floating)):
                return "\u2014" if np.isnan(float(v)) else _f(v)
            return str(v)
        rows = [[_icc_row_cell(v) for v in icc.loc[i]] for i in icc.index]

        # ── BUGFIX (fatal, confirmed via audit): the previous headline
        # selection used icc["Type"].str.contains("k"), which matches
        # ICC(1,k), ICC(A,k), AND ICC(C,k) (all three contain the letter
        # "k"), then took .iloc[0] — the FIRST matching row in pingouin's
        # fixed output order, which is ICC(1,k) (one-way random). This
        # produced a headline "internal consistency" metric drawn from a
        # ONE-WAY model, which assumes each subject is rated by a
        # DIFFERENT randomly-selected set of items — the opposite of a
        # questionnaire design, where every respondent answers the exact
        # same fixed set of items (a two-way, fixed-items design).
        # Cronbach's alpha is mathematically identical to ICC(C,k)
        # [two-way mixed effects, CONSISTENCY, average measures] — NOT
        # to ICC(1,k) or ICC(A,k). Verified with a realistic test case
        # (heterogeneous item means): the old buggy selection produced
        # ICC(1,k) = -0.110 ("Poor"), while the correct ICC(C,k) = 0.773
        # ("Good") — a 0.883 gap capable of reversing a published
        # reliability conclusion. Fixed to an EXPLICIT key lookup,
        # identical in style to how the Inter-Rater Agreement context
        # already correctly selects icc_2_1 by exact key (never had this
        # bug) rather than by fuzzy string matching.
        ck_row = icc[icc["Type"] == "ICC(C,k)"]
        head = float(ck_row["ICC"].iloc[0]) if not ck_row.empty else np.nan
        head_ci_row = ck_row
        head_p = float(head_ci_row["pval"].iloc[0]) if (not head_ci_row.empty and "pval" in head_ci_row.columns) else np.nan

        a_val = res.get("alpha", np.nan)
        n_val = res.get("n", "\u2014"); k_val = res.get("k", "\u2014")
        avg_r = res.get("avg_inter_item_r", np.nan)
        alpha_gap = (abs(head - a_val) if (not (isinstance(head, float) and np.isnan(head))
                     and not (isinstance(a_val, float) and np.isnan(a_val))) else np.nan)

        icc_deleted_df = res.get("icc_if_deleted")
        has_deleted = icc_deleted_df is not None and not icc_deleted_df.empty
        deleted_table = None
        if has_deleted:
            deleted_table = (["Item", "ICC(C,k) if Item Deleted"],
                              [[r["Item"], _f(r["ICC(C,k) if Item Deleted"])]
                               for _, r in icc_deleted_df.iterrows()])

        primary_section = {
            "heading": "Primary Result \u2014 ICC(C,k)",
            "cards": [("ICC(C,k) \u2014 Primary", _f(head), _icc_label(head)),
                      ("Cronbach's \u03b1 (cross-check)", _f(a_val), alpha_label(a_val)),
                      ("Mean Inter-Item r", _f(avg_r), "")],
            "table": (["Statistic", "Value"], [
                ["N (respondents)", str(n_val)],
                ["k (items)", str(k_val)],
                ["ICC(C,k)", _f(head)],
                ["p (F-test)", _fmt_p_dash(head_p)],
                ["Cronbach's \u03b1 (same scale, covariance-ratio estimator)", _f(a_val)],
                ["|ICC(C,k) \u2212 \u03b1|", _f(alpha_gap)],
                ["Mean Inter-Item Correlation", _f(avg_r)],
            ]),
            "table2": deleted_table,
            "table2_note": ("Each row: ICC(C,k) recomputed with that item removed \u2014 "
                             "the ANOVA-based analogue of \u2018Cronbach\u2019s alpha if item "
                             "deleted\u2019. A value ABOVE the full-scale ICC(C,k) "
                             f"({_f(head)}) indicates removing that item would improve "
                             "consistency; requires \u22654 items."
                             if has_deleted else ""),
            "params": ("MODEL: two-way MIXED effects, CONSISTENCY, average measures "
                       "\u2014 the model that matches a fixed-items questionnaire design, "
                       "where every respondent answers the identical set of items (not "
                       "a randomly-varying set per respondent). This is the ICC form "
                       "that is mathematically identical to Cronbach's alpha (both "
                       "equal (MSB\u2212MSE)/MSB from the same two-way ANOVA "
                       "decomposition, without the between-item/column mean square "
                       "in the formula) \u2014 the near-zero gap above is the expected, "
                       "verifiable signature of that identity, not a coincidence. "
                       "Koo & Li (2016): <0.50 poor; 0.50\u20130.75 moderate; "
                       "0.75\u20130.90 good; >0.90 excellent."),
            "interp": (f"ICC(C,k) = {_f(head)}, indicating <b>{_icc_label(head)}</b> "
                       f"internal consistency \u2014 mathematically the same quantity as "
                       f"Cronbach's \u03b1 ({_f(a_val)}), confirmed above by their small "
                       f"numerical gap ({_f(alpha_gap)}), computed here via an explicit "
                       f"two-way ANOVA decomposition (Shrout & Fleiss, 1979) rather "
                       f"than the covariance-ratio formula. Use average measures "
                       f"(\u2018k\u2019) \u2014 not single measures (\u20181\u2019) \u2014 as the "
                       f"mandatory standard for overall scale reliability: single-"
                       f"measures forms evaluate the reliability of one individual "
                       f"item alone, not the combined scale."),
            "note": ("WHEN TO USE THIS (IC) CONTEXT vs the Inter-Rater Agreement "
                     "module's ICC: use this context when your question is about "
                     "item-level internal consistency of a scale; use the Inter-Rater "
                     "Agreement module when your question is about agreement between "
                     "distinct raters assessing the same units. Both contexts share "
                     "identical underlying mathematics (Shrout & Fleiss, 1979) but "
                     "answer different substantive questions, and by design select "
                     "DIFFERENT primary forms: this context selects ICC(C,k) "
                     "(consistency, matching Cronbach's alpha); the Inter-Rater "
                     "Agreement context selects ICC(A,1)/ICC(2,1) (absolute "
                     "agreement, penalising systematic rater bias) \u2014 see the "
                     "reference guide below for the full six-form breakdown. "
                     "Reference: Shrout, P.E., & Fleiss, J.L. (1979). Psychological "
                     "Bulletin, 86(2), 420\u2013428."),
        }

        # ── Structured reference guide: all six ICC forms ──────────────────
        # Content specified per explicit user requirement: for each form,
        # When to Use / Model Parameters / Academic Reference, tabulated
        # together so a user can see all six side by side rather than only
        # the one being used as the headline.
        reference_table = (
            ["Form", "Model", "Agreement Type", "Unit", "When to Use", "Reference"],
            [
                ["ICC(1,1)", "One-way random", "Absolute agreement", "Single",
                 "Different, randomly-selected items/raters evaluate each subject; "
                 "unit of interest is a single item/rater.",
                 "Shrout & Fleiss (1979); McGraw & Wong (1996)"],
                ["ICC(A,1)\n[ICC(2,1)]", "Two-way random", "Absolute agreement", "Single",
                 "The same set of random items/raters evaluate all subjects, and "
                 "exact score agreement (incl. systematic bias) for a single item matters.",
                 "McGraw & Wong (1996); Koo & Li (2016)"],
                ["ICC(C,1)\n[ICC(3,1)]", "Two-way mixed", "Consistency", "Single",
                 "The same items evaluate all subjects, measuring rank-order "
                 "consistency of a single item while ignoring systematic mean differences.",
                 "Shrout & Fleiss (1979)"],
                ["ICC(1,k)", "One-way random", "Absolute agreement", "Average (k)",
                 "Different items/raters assess each subject, and the target score "
                 "is the average across all k items.",
                 "Shrout & Fleiss (1979)"],
                ["ICC(A,k)\n[ICC(2,k)]", "Two-way random", "Absolute agreement", "Average (k)",
                 "The same items evaluate all subjects, assessing absolute agreement "
                 "of the overall scale score (average of k items) including systematic "
                 "item differences.",
                 "McGraw & Wong (1996); Koo & Li (2016)"],
                ["ICC(C,k)\n[ICC(3,k)] \u2014 PRIMARY HERE", "Two-way mixed", "Consistency", "Average (k)",
                 "STANDARD METRIC for scale internal consistency (Cronbach's alpha "
                 "equivalent). Evaluates consistency of the averaged scale score "
                 "when all subjects answer the same fixed items.",
                 "Shrout & Fleiss (1979); McGraw & Wong (1996); Koo & Li (2016)"],
            ])
        full_results_section = {
            "heading": "Full Results \u2014 All Six ICC Forms",
            "table": (cols, rows),
            "table_left": {0},
            "note": ("Complete numeric output (value, F, df1, df2, p, 95% CI) for "
                     "all six ICC forms, as returned by pingouin.intraclass_corr(). "
                     "ICC(C,k) (highlighted in the Primary Result above) is the "
                     "recommended headline metric for internal consistency; the "
                     "remaining five forms are provided here in full for "
                     "transparency and for researchers who need single-measures "
                     "forms, absolute-agreement forms, or one-way forms for a "
                     "specific purpose. See the Reference Guide below for when "
                     "each form is appropriate."),
        }

        reference_section = {
            "heading": "Reference Guide \u2014 All Six ICC Variants",
            "table": reference_table,
            "table_left": {0, 1, 2, 3, 4, 5},
            "note": ("Interpretation benchmarks (Koo & Li, 2016), applied identically "
                     "to all six forms: <0.50 poor; 0.50\u20130.75 moderate; 0.75\u20130.90 "
                     "good; >0.90 excellent \u2014 presented as a sourced heuristic, not "
                     "a universal statistical law. Full numeric result table for all "
                     "six computed forms (value, F, df1, df2, p, 95% CI) is provided "
                     "in the \u2018Full Results\u2019 section above."),
        }

        blocks.append({
            "key": "ICC", "title": "Intraclass Correlation Coefficient",
            "sections": [primary_section, full_results_section, reference_section],
            "cards": [], "table": None, "interp": "", "params": "", "note": "",
        })

    return blocks


def _item_tables(res):
    out = {}
    its = res.get("item_descriptives")
    if its is not None and not its.empty:
        out["Item Statistics"] = (list(its.columns),
            [[_f(v) if isinstance(v, (int, float, np.floating)) else str(v)
              for v in its.loc[i]] for i in its.index])
    summ = res.get("summary_item_stats")
    if summ is not None and not summ.empty:
        out["Summary Item Statistics"] = (list(summ.columns),
            [[_f(v) if isinstance(v, (int, float, np.floating)) else str(v)
              for v in summ.loc[i]] for i in summ.index])
    itot = res.get("item_stats")
    if itot is not None and not itot.empty:
        out["Item-Total Statistics"] = (list(itot.columns),
            [[_f(v) if isinstance(v, (int, float, np.floating)) else str(v)
              for v in itot.loc[i]] for i in itot.index],
            bool(itot.attrs.get("has_negative_alpha")))
    iic = res.get("inter_item_corr")
    if iic is not None and not iic.empty:
        out["Inter-Item Correlation Matrix"] = ([""] + list(iic.columns),
            [[idx] + [_f(v) for v in iic.loc[idx]] for idx in iic.index])
    return out


def _scale_rows(res):
    s = res.get("scale_stats", {})
    return (["Statistic", "Value"],
            [["Mean", _f(s.get("mean"))], ["Median", _f(s.get("median"))],
             ["Variance", _f(s.get("variance"))],
             ["Std. Deviation", _f(s.get("sd"))],
             ["Minimum", _f(s.get("min"))], ["Maximum", _f(s.get("max"))],
             ["Range", _f(s.get("range"))],
             ["Skewness", _f(s.get("skewness"))],
             ["Kurtosis", _f(s.get("kurtosis"))],
             ["N of Items", str(s.get("k", ""))],
             ["N of Cases", str(s.get("n", ""))]])


# ══════════════════════════════════════════════════════════════════════════════
# METHODOLOGICAL NOTES (shared)
# ══════════════════════════════════════════════════════════════════════════════

def _methodological_notes_ic(M, alpha):
    """Methodological notes specific to Internal Consistency analysis."""
    pct = int((1 - alpha) * 100)
    rm = M.get("reverse_method")
    rm_name = {"theoretical": "theoretical scale endpoints ((min+max) − x)",
               "observed": "observed min/max ((min+max) − x)",
               "zscore": "z-score reversal (−z)"}.get(rm, "none (reversal off)")
    return [
        ("Cronbach's Alpha",
         "α = (k/(k−1))(1 − Σ s²ᵢ / s²_total). Standardised alpha uses the "
         "inter-item correlation matrix. The "
         f"{pct}% CI uses the Feldt (1965) F-based method. "
         "Interpretation benchmarks (George & Mallery, 2003): "
         "α ≥ .90 Excellent; .80–.89 Good; .70–.79 Acceptable; "
         ".60–.69 Questionable; .50–.59 Poor; < .50 Unacceptable."),
        ("McDonald's Omega",
         "Estimated from single-factor loadings (one-factor congeneric model). "
         "ω = (Σλᵢ)² / ((Σλᵢ)² + Σθᵢᵢ), where λᵢ are factor loadings and "
         "θᵢᵢ are unique variances. Preferred over α when items are not "
         "strictly tau-equivalent (unequal true-score variances). "
         "Reference: McDonald (1999). Test Theory: A Unified Treatment."),
        ("Guttman's Lambda",
         "λ₁–λ₆ from the covariance matrix. λ₃ = Cronbach's α. "
         "λ₂ is frequently the tightest lower bound to reliability. "
         "λ₆ (corrected split-half) requires an invertible item correlation matrix. "
         "Reference: Guttman (1945). Psychometrika."),
        ("Split-Half Reliability",
         "First half vs second half of items; "
         "Spearman-Brown formula assumes equal-length, parallel halves; "
         "Guttman split-half does not require this assumption. "
         "Reference: Spearman (1910); Brown (1910)."),
        ("KR-20",
         "Kuder-Richardson Formula 20 — the special case of Cronbach's α "
         "for strictly dichotomous (0/1) items. "
         "KR-20 = (k/(k−1)) × (1 − Σ(pᵢqᵢ) / s²_total). "
         "Reported automatically only when all items are 0/1 coded. "
         "Reference: Kuder & Richardson (1937). Psychometrika."),
        ("Intraclass Correlation (ICC)",
         "Two-way ANOVA decomposition (pingouin; Shrout & Fleiss, 1979). "
         "Six standard forms reported: ICC(1,1), ICC(A,1), ICC(C,1) "
         "for single-rater, and ICC(1,k), ICC(A,k), ICC(C,k) for mean of k raters. "
         "Absolute agreement (A) penalises systematic rater bias; "
         "consistency (C) does not. "
         "Benchmarks (Koo & Li, 2016): < .50 Poor; .50–.75 Moderate; "
         ".75–.90 Good; > .90 Excellent."),
        ("Item-Total Statistics",
         "Corrected item-total correlation (r_it): Pearson correlation of the item "
         "with the sum of remaining items. r_it < .30 suggests weak discrimination. "
         "Squared multiple correlation (R²): proportion of item variance explained "
         "by all other items. α-if-deleted: Cronbach's α computed with the item removed; "
         "a value exceeding the full-scale α indicates the item reduces reliability. "
         "Negative α-if-deleted values are flagged (footnote a) and signal model "
         "violations (e.g., un-reversed reverse-coded items)."),
        ("Reverse-Scored Items",
         f"Reversal method applied: {rm_name}. Items with negative corrected "
         "item-total correlations are automatically flagged. Reversal is OFF by "
         "default; when enabled, the exact items reversed and the formula used "
         "are reported per construct."),
        ("Missing Data",
         "Listwise deletion per construct: only cases with complete data across "
         "all items in a construct are included. N per construct is reported."),
        ("Interpretation Thresholds",
         "Cronbach's α / McDonald's ω (George & Mallery, 2003): "
         "≥ .90 Excellent; .80–.89 Good; .70–.79 Acceptable; "
         ".60–.69 Questionable; .50–.59 Poor; < .50 Unacceptable. "
         "ICC (Koo & Li, 2016): < .50 Poor; .50–.75 Moderate; "
         ".75–.90 Good; > .90 Excellent."),
        ("References",
         "Cronbach (1951) Psychometrika; Kuder & Richardson (1937) Psychometrika; "
         "Guttman (1945) Psychometrika; Feldt (1965) Psychometrika; "
         "Shrout & Fleiss (1979) Psychological Bulletin; McDonald (1999); "
         "George & Mallery (2003); Koo & Li (2016) Journal of Chiropractic Medicine."),
    ]


def _methodological_notes_irar(M, alpha):
    """Methodological notes specific to Inter-Rater Agreement analysis."""
    pct = int((1 - alpha) * 100)
    constructs = M.get("constructs", [])
    if not constructs:
        return []
    # Gather all methods computed across all groups
    all_methods = set()
    for c in constructs:
        all_methods.update(c.get("applicable_methods", []))

    notes = []
    notes.append((
        "Percentage Agreement",
        "Observed proportion of exact pairwise agreements across all rater pairs. "
        "PA = (number of agreements) / (total pairwise comparisons). "
        "Does not correct for chance agreement and therefore should always be "
        "reported alongside a chance-corrected index. "
        "Reported here as a descriptive baseline. "
        "Reference: Stemler (2004). Practical Assessment, Research & Evaluation, 9(4)."
    ))

    if "cohen" in all_methods:
        notes.append((
            "Cohen's Kappa (κ)",
            "κ = (P_o − P_e) / (1 − P_e). P_o = observed agreement; "
            "P_e = expected agreement by chance = Σ p_c(r1) × p_c(r2). "
            "SE via Fleiss, Cohen & Everitt (1969); z-test; two-tailed p. "
            "Known limitation: κ can be paradoxically low when one category "
            "dominates (prevalence paradox) or when raters differ in marginal "
            "distributions (bias paradox). "
            "Benchmarks (Landis & Koch, 1977): < 0 Poor; 0.00–0.20 Slight; "
            "0.21–0.40 Fair; 0.41–0.60 Moderate; 0.61–0.80 Substantial; "
            "0.81–1.00 Almost Perfect. "
            "Reference: Cohen (1960). Educational and Psychological Measurement, 20(1)."
        ))

    if "gwet_ac1" in all_methods:
        notes.append((
            "Gwet's AC1",
            "AC1 = (P_o − P_e_AC1) / (1 − P_e_AC1). "
            "P_e(AC1) = (1/(q−1)) × Σ_c π_c(1−π_c), where π_c is the grand "
            "marginal proportion of category c across all raters. "
            "More stable than Cohen's κ under extreme marginal distributions "
            "(avoids the prevalence paradox). Variance estimated via jackknife. "
            "Benchmarks: same as Cohen's κ (Landis & Koch, 1977). "
            "References: Gwet (2008). British Journal of Mathematical and Statistical "
            "Psychology, 61(1), 29–48. Gwet (2014). Handbook of Inter-Rater Reliability (4th ed.)."
        ))

    if "scott_pi" in all_methods:
        notes.append((
            "Scott's Pi (π)",
            "π = (P_o − P_e_scott) / (1 − P_e_scott). "
            "P_e(Scott) = Σ_c ((p_c(r1) + p_c(r2))/2)², using averaged (pooled) "
            "marginal proportions rather than their product. "
            "Differs from Cohen's κ only in P_e computation; typically yields "
            "slightly lower estimates when rater marginals differ. "
            "SE: asymptotic approximation (Fleiss et al., 1969). "
            "Reference: Scott (1955). Public Opinion Quarterly, 19(3), 321–325."
        ))

    if "bp" in all_methods:
        notes.append((
            "Brennan-Prediger Coefficient (κ_BP)",
            "κ_BP = (P_o − 1/q) / (1 − 1/q). Assumes uniform category distribution "
            f"(P_e = 1/q) — the most conservative expected agreement. "
            "Appropriate when categories are equally likely a priori (e.g., "
            "forced-choice classification tasks). Avoids both the prevalence and "
            "bias paradoxes that affect Cohen's κ. "
            "Reference: Brennan & Prediger (1981). Educational and Psychological "
            "Measurement, 41(3), 687–699."
        ))

    if "fleiss" in all_methods:
        notes.append((
            "Fleiss' Kappa (κ)",
            "Generalises Cohen's κ to ≥ 3 raters. "
            "κ = (P̄ − P̄_e) / (1 − P̄_e). "
            "P̄ = mean per-unit agreement across all rater pairs; "
            "P̄_e = Σ_c p̄²_c (expected by chance). "
            "Per-category κ_j also reported. "
            "Note: Fleiss' κ treats all categories as nominal (unordered). "
            "For ordinal multi-rater data, Gwet's AC2 or Krippendorff's α "
            "(ordinal metric) is preferred. "
            "Reference: Fleiss (1971). Psychological Bulletin, 76(5), 378–382."
        ))

    if "weighted" in all_methods:
        notes.append((
            "Weighted Cohen's Kappa (κ_w)",
            "κ_w = 1 − Σ w_cc' d_cc' / Σ w_cc' e_cc'. "
            "Quadratic weights: w_cc' = 1 − (c−c')² / (q−1)². "
            "Linear weights: w_cc' = 1 − |c−c'| / (q−1). "
            "Quadratic weights recommended for Likert-type scales — larger "
            "disagreements are penalised proportionally more. "
            "Note: κ_w (quadratic) ≈ ICC(A,1) for continuous data. "
            "Reference: Cohen (1968). Psychological Bulletin, 70(4), 213–220."
        ))

    if "gwet_ac2" in all_methods:
        notes.append((
            "Gwet's AC2",
            "Weighted version of AC1 for ordinal data, computed under all five "
            "standard weighting schemes (Quadratic/Fleiss-Cohen, Linear/Cicchetti-"
            "Allison, Radical, Ordinal/Krippendorff-style, and Identity) — see the "
            "AC2 tab for the complete set with individual guidance and references. "
            "AC2 = (P_o_w − P_e_w) / (1 − P_e_w). "
            "P_e_w = u × Σ_k π_k(1−π_k) / (q(q−1)), where u = the sum of every "
            "cell of the q×q weight matrix (including the diagonal) and q = the "
            "user-declared number of categories in the coding scheme. This "
            "formula is verified to reduce exactly to AC1's own P_e formula "
            "when Identity (unweighted) weights are used. "
            "More stable than Weighted Cohen's κ under unequal marginals. "
            "Variance estimated via jackknife. "
            "Reference: Gwet (2014). Handbook of Inter-Rater Reliability (4th ed.), Chapter 5."
        ))

    if "icc" in all_methods:
        notes.append((
            "Intraclass Correlation Coefficient (ICC)",
            "Two-way ANOVA decomposition (pingouin; Shrout & Fleiss, 1979). "
            "Six forms: ICC(1,1) one-way random; ICC(A,1) two-way random absolute, "
            "single rater [PRIMARY for single-rater reliability]; "
            "ICC(C,1) two-way mixed consistency, single rater; "
            "ICC(1,k), ICC(A,k), ICC(C,k) = corresponding average-of-k forms. "
            "Absolute agreement (A) penalises systematic rater bias; "
            f"consistency (C) does not. {pct}% CI via F-distribution. "
            "Benchmarks (Koo & Li, 2016): < .50 Poor; .50–.75 Moderate; "
            ".75–.90 Good; > .90 Excellent. "
            "Reference: Shrout & Fleiss (1979). Psychological Bulletin, 86(2)."
        ))

    if "ccc" in all_methods:
        notes.append((
            "Lin's Concordance Correlation Coefficient (CCC / ρ_c)",
            "ρ_c = 2σ_xy / (σ_x² + σ_y² + (μ_x−μ_y)²) = ρ × C_b. "
            "ρ = Pearson correlation (precision); "
            "C_b = bias correction factor (accuracy). "
            "CCC simultaneously evaluates how tightly raters agree (precision) "
            "and how close their scores are to the line of perfect concordance (accuracy). "
            "CCC ≤ Pearson r always; the gap between them reflects systematic bias. "
            f"{pct}% CI via Fisher z-transformation. "
            "Benchmarks (Koo & Li, 2016 adapted): ρ_c > .90 Excellent; "
            ".75–.90 Good; .50–.75 Moderate; < .50 Poor. "
            "References: Lin (1989). Biometrics, 45(1), 255–268. "
            "Carrasco & Jover (2003). Statistics in Medicine, 22(1), 163–175."
        ))

    if "krippendorff" in all_methods:
        notes.append((
            "Krippendorff's Alpha (α)",
            "α = 1 − D_o/D_e. D_o = observed disagreement (mean pairwise distance "
            "within units); D_e = expected disagreement (mean pairwise distance "
            "across all values). Distance metric varies by data type: "
            "nominal d(a,b)=0/1; ordinal d(a,b)=(Σn_g from a to b − (n_a+n_b)/2)²; "
            "interval d(a,b)=(a−b)²; ratio d(a,b)=((a−b)/(a+b))². "
            "Handles missing data and any number of raters. "
            f"{pct}% CI: percentile bootstrap (1,000 resamples, seed=42). "
            "Thresholds (Krippendorff, 2004): α ≥ .800 reliable; "
            ".667 ≤ α < .800 tentatively acceptable; α < .667 unreliable. "
            "Reference: Krippendorff (2004). Content Analysis (2nd ed.)."
        ))

    notes.append((
        "Agreement Benchmarks — Summary",
        "Kappa family (Landis & Koch, 1977): < 0 Poor; 0.00–0.20 Slight; "
        "0.21–0.40 Fair; 0.41–0.60 Moderate; 0.61–0.80 Substantial; "
        "0.81–1.00 Almost Perfect. "
        "ICC / CCC (Koo & Li, 2016): < .50 Poor; .50–.75 Moderate; "
        ".75–.90 Good; > .90 Excellent. "
        "Krippendorff's α: ≥ .800 reliable; .667–.800 tentatively acceptable. "
        "Note: Percentage Agreement does not correct for chance and should "
        "not be used as a standalone reliability index."
    ))

    notes.append((
        "Missing Data",
        "Listwise deletion per rating group: only units with complete ratings "
        "from all raters are included. N per group is reported."
    ))

    return notes


def _methodological_notes(M, alpha):
    """Route to IC or IRAR methodological notes based on analysis mode."""
    if M.get("analysis_mode") == "Inter-Rater Agreement":
        return _methodological_notes_irar(M, alpha)
    return _methodological_notes_ic(M, alpha)




# ══════════════════════════════════════════════════════════════════════════════
# PLOTS
# ══════════════════════════════════════════════════════════════════════════════

def _alpha_bar(summary):
    names = summary["Construct"].tolist()
    vals = [float(v) if v == v else 0 for v in summary["Cronbach's \u03b1"]]
    fig, ax = plt.subplots(figsize=(7, max(2.2, 0.6 * len(names) + 1)))
    colors = ["#16a34a" if v >= .8 else "#0284c7" if v >= .7
              else "#f59e0b" if v >= .6 else "#dc2626" for v in vals]
    ax.barh(names, vals, color=colors, edgecolor="white")
    for thr in (.7, .8, .9):
        ax.axvline(thr, color="#94a3b8", ls="--", lw=.8)
    ax.set_xlim(0, 1); ax.set_xlabel("Cronbach's \u03b1", fontsize=9, color=PAL[0])
    ax.set_title("Reliability by Construct", fontsize=11, fontweight="bold", color=PAL[0])
    for i, v in enumerate(vals):
        ax.text(min(v + .02, .95), i, f"{v:.3f}", va="center", fontsize=8, color=PAL[0])
    ax.spines[["top", "right"]].set_visible(False)
    fig.patch.set_facecolor("white"); fig.tight_layout()
    return fig


def _item_total_plot(res):
    its = res.get("item_stats")
    if its is None or its.empty:
        return None
    items = its["Item"].tolist()
    vals = [float(v) if v == v else 0 for v in its["Corrected Item-Total Correlation"]]
    fig, ax = plt.subplots(figsize=(7, max(2, 0.5 * len(items) + 1)))
    colors = ["#dc2626" if v < 0 else "#0284c7" if v < .3 else "#16a34a" for v in vals]
    ax.barh(items, vals, color=colors, edgecolor="white")
    ax.axvline(.3, color="#94a3b8", ls="--", lw=.8)
    ax.axvline(0, color="#1a1a2e", lw=.8)
    ax.set_xlabel("Corrected Item-Total Correlation", fontsize=9, color=PAL[0])
    ax.set_title(f"Item Discrimination \u2014 {res['construct_name']}",
                 fontsize=10, fontweight="bold", color=PAL[0])
    ax.spines[["top", "right"]].set_visible(False)
    fig.patch.set_facecolor("white"); fig.tight_layout()
    return fig


def _irar_icc_bar(icc_res, title="ICC — All Forms"):
    """Bar chart of all 6 ICC forms — bbox labels, no overlap."""
    forms  = ["ICC(1,1)\nOne-way random\n1 rater",
              "ICC(A,1) ★ PRIMARY\nTwo-way random\nAbsolute, 1 rater",
              "ICC(C,1)\nTwo-way mixed\nConsistency, 1 rater",
              "ICC(1,k)\nOne-way random\nMean of k raters",
              "ICC(A,k)\nTwo-way random\nAbsolute, mean",
              "ICC(C,k)\nTwo-way mixed\nConsistency, mean"]
    keys   = ["icc_1_1","icc_2_1","icc_3_1","icc_1_k","icc_2_k","icc_3_k"]
    real_vals = []
    for k in keys:
        v = icc_res.get(k, np.nan)
        try:    real_vals.append(float(v) if not np.isnan(float(v)) else np.nan)
        except: real_vals.append(np.nan)
    disp = [max(min(v,1.0),-0.30) if not np.isnan(v) else 0.0 for v in real_vals]
    def _col(v):
        if np.isnan(v): return "#cbd5e1"
        if v>=.90: return "#16a34a"
        if v>=.75: return "#0284c7"
        if v>=.50: return "#f59e0b"
        return "#dc2626"
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.barh(forms, disp, color=[_col(v) for v in real_vals],
            edgecolor="white", height=0.52, zorder=3)
    for thr, col in [(0.50,"#f59e0b"),(0.75,"#0284c7"),(0.90,"#16a34a")]:
        ax.axvline(thr, color=col, ls="--", lw=0.9, alpha=0.45, zorder=1)
    ax.axvline(0, color="#334155", lw=0.9, zorder=2)
    ax.set_xlim(-0.42, 1.32)
    ax.set_xlabel("ICC value", fontsize=9, color=PAL[0])
    ax.set_title(title + "\n★ Primary: ICC(A,1) — absolute agreement, single rater"
                 "  |  Benchmarks (Koo & Li, 2016): <0.50 Poor · 0.50–0.75 Moderate · "
                 "0.75–0.90 Good · >0.90 Excellent",
                 fontsize=7.5, color=PAL[0], pad=8)
    for i, (rv, dv) in enumerate(zip(real_vals, disp)):
        if not np.isnan(rv):
            lx = dv+0.04 if dv>=0 else dv-0.04
            ha = "left" if dv>=0 else "right"
            ax.text(lx, i, f"{rv:.3f}", va="center", ha=ha,
                    fontsize=9, fontweight="bold", color=PAL[0], zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white",
                              ec="none", alpha=0.88))
    ax.spines[["top","right"]].set_visible(False)
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=1.5)
    return fig


def _irar_kripp_gauge(alpha_val, label, title="Krippendorff's α"):
    """Horizontal gauge — colour zones, bbox label, zero overlap."""
    fig, ax = plt.subplots(figsize=(8.5, 2.8))
    ax.set_xlim(-0.15, 1.10); ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.spines[["top","right","left"]].set_visible(False)
    ax.barh([0.5],[0.667],left=-0.15,height=0.38,color="#fee2e2",alpha=0.50,zorder=1)
    ax.barh([0.5],[0.133],left=0.667,height=0.38,color="#fef9c3",alpha=0.50,zorder=1)
    ax.barh([0.5],[0.233],left=0.800,height=0.38,color="#dcfce7",alpha=0.50,zorder=1)
    for mid, col, lbl in [(0.26,"#dc2626","Unreliable"),
                           (0.733,"#ca8a04","Tentative"),
                           (0.900,"#16a34a","Reliable")]:
        ax.text(mid, 0.50, lbl, ha="center", va="center", fontsize=7.5,
                color=col, alpha=0.65,
                transform=ax.get_xaxis_transform(), zorder=2)
    for thr, col, lbl in [(0.667,"#ca8a04","0.667"),(0.800,"#16a34a","0.800")]:
        ax.axvline(thr, color=col, lw=1.8, zorder=4, alpha=0.85)
        ax.text(thr, 0.97, lbl, ha="center", va="top", fontsize=8.5,
                color=col, fontweight="bold",
                transform=ax.get_xaxis_transform(), zorder=5,
                bbox=dict(boxstyle="round,pad=0.20",fc="white",ec="none",alpha=0.88))
    try:
        av = float(alpha_val)
        if not np.isnan(av):
            av_c = max(min(av,1.07),-0.12)
            col = "#16a34a" if av>=.80 else "#ca8a04" if av>=.667 else "#dc2626"
            ax.plot([av_c],[0.50],marker="v",markersize=22,color=col,zorder=6)
            ax.text(av_c,0.91,f"α = {av:.3f}",ha="center",va="top",
                    fontsize=11,fontweight="bold",color=col,
                    transform=ax.get_xaxis_transform(),zorder=7,
                    bbox=dict(boxstyle="round,pad=0.30",fc="white",
                              ec=col,alpha=0.97,lw=1.5))
    except Exception:
        pass
    ax.set_xlabel("Krippendorff's α", fontsize=9, color=PAL[0])
    ax.set_title(f"{title} — {label}", fontsize=10, fontweight="bold",
                 color=PAL[0], pad=8)
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=1.3)
    return fig


def _irar_pa_gauge(pa_val, ci_lo, ci_hi, title="Percentage Agreement"):
    """Gauge for % Agreement — same readability standard as Kripp gauge."""
    fig, ax = plt.subplots(figsize=(8.5, 2.8))
    ax.set_xlim(-0.02, 1.10); ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.spines[["top","right","left"]].set_visible(False)
    ax.barh([0.5],[0.70],left=0.0, height=0.38,color="#fee2e2",alpha=0.50,zorder=1)
    ax.barh([0.5],[0.10],left=0.70,height=0.38,color="#fef9c3",alpha=0.50,zorder=1)
    ax.barh([0.5],[0.10],left=0.80,height=0.38,color="#bbf7d0",alpha=0.50,zorder=1)
    ax.barh([0.5],[0.10],left=0.90,height=0.38,color="#dcfce7",alpha=0.60,zorder=1)
    for mid, col, lbl in [(0.35,"#dc2626","Low"),
                           (0.75,"#ca8a04","Fair"),
                           (0.85,"#0284c7","Good"),
                           (0.95,"#16a34a","High")]:
        ax.text(mid, 0.50, lbl, ha="center", va="center", fontsize=7.5,
                color=col, alpha=0.65,
                transform=ax.get_xaxis_transform(), zorder=2)
    for thr, col, lbl in [(0.70,"#f59e0b","70%"),(0.80,"#0284c7","80%"),(0.90,"#16a34a","90%")]:
        ax.axvline(thr, color=col, lw=1.8, zorder=4, alpha=0.85)
        ax.text(thr, 0.97, lbl, ha="center", va="top", fontsize=8.5,
                color=col, fontweight="bold",
                transform=ax.get_xaxis_transform(), zorder=5,
                bbox=dict(boxstyle="round,pad=0.20",fc="white",ec="none",alpha=0.88))
    try:
        pv = float(pa_val)
        if not np.isnan(pv):
            pv_c = max(min(pv,1.07),0.0)
            col = ("#16a34a" if pv>=.90 else "#0284c7" if pv>=.80
                   else "#f59e0b" if pv>=.70 else "#dc2626")
            ax.plot([pv_c],[0.50],marker="v",markersize=22,color=col,zorder=6)
            lbl_txt = f"PA = {pv*100:.1f}%"
            try:
                if not (np.isnan(float(ci_lo)) or np.isnan(float(ci_hi))):
                    lbl_txt += f"\n95% CI [{float(ci_lo)*100:.1f}–{float(ci_hi)*100:.1f}%]"
            except Exception:
                pass
            ax.text(pv_c,0.91,lbl_txt,ha="center",va="top",fontsize=10,
                    fontweight="bold",color=col,
                    transform=ax.get_xaxis_transform(),zorder=7,
                    bbox=dict(boxstyle="round,pad=0.30",fc="white",
                              ec=col,alpha=0.97,lw=1.5))
    except Exception:
        pass
    ax.set_xlabel("Percentage Agreement", fontsize=9, color=PAL[0])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x*100:.0f}%"))
    ax.set_title(title, fontsize=10, fontweight="bold", color=PAL[0], pad=8)
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=1.3)
    return fig


def _irar_single_bar(value, label, method_name, group_name,
                     benchmarks=None, xlim=(-0.22, 1.12)):
    """Universal single-value bar — bbox label, no line overlap."""
    if benchmarks is None:
        benchmarks = [(0.20,"#94a3b8"),(0.40,"#f59e0b"),
                      (0.60,"#0284c7"),(0.80,"#16a34a")]
    try:    fv = float(value)
    except: fv = np.nan
    dv = max(min(fv,xlim[1]-0.06),xlim[0]+0.06) if not np.isnan(fv) else 0.0
    col = ("#16a34a" if not np.isnan(fv) and fv>=.80 else
           "#0284c7" if not np.isnan(fv) and fv>=.60 else
           "#f59e0b" if not np.isnan(fv) and fv>=.40 else "#dc2626")
    fig, ax = plt.subplots(figsize=(8.5, 1.85))
    ax.barh([method_name],[dv],color=col if not np.isnan(fv) else "#cbd5e1",
            edgecolor="white",height=0.45,zorder=3)
    for thr, tcol in benchmarks:
        ax.axvline(thr,color=tcol,ls="--",lw=0.9,alpha=0.45,zorder=1)
    ax.axvline(0,color="#334155",lw=0.9,zorder=2)
    ax.set_xlim(xlim)
    ax.set_xlabel("Value",fontsize=9,color=PAL[0])
    ax.set_title(f"{method_name} = {fv:.3f} — {label} — {group_name}",
                 fontsize=10,fontweight="bold",color=PAL[0],pad=6)
    if not np.isnan(fv):
        lx = dv+0.04 if dv>=0 else dv-0.04
        ha = "left" if dv>=0 else "right"
        ax.text(lx,0,f"{fv:.3f}",va="center",ha=ha,
                fontsize=11,fontweight="bold",color=PAL[0],zorder=5,
                bbox=dict(boxstyle="round,pad=0.25",fc="white",ec="none",alpha=0.92))
    ax.set_yticks([])
    ax.spines[["top","right","left"]].set_visible(False)
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=1.2)
    return fig


def _irar_kappa_heatmap(ct_df, r1_name="Rater 1", r2_name="Rater 2",
                         title="Confusion Matrix"):
    """Heatmap — contrast cell text, colorbar outside, no overlap."""
    if ct_df is None or ct_df.empty: return None
    n = max(len(ct_df.columns), len(ct_df.index))
    sz = max(3.8, 0.95*n + 1.4)
    fig, ax = plt.subplots(figsize=(sz+1.2, sz))
    arr = ct_df.values.astype(float)
    im = ax.imshow(arr, cmap="Blues", aspect="auto", vmin=0)
    ax.set_xticks(range(len(ct_df.columns)))
    ax.set_xticklabels(ct_df.columns, fontsize=9)
    ax.set_yticks(range(len(ct_df.index)))
    ax.set_yticklabels(ct_df.index, fontsize=9)
    ax.set_xlabel(r2_name, fontsize=9, color=PAL[0], labelpad=7)
    ax.set_ylabel(r1_name, fontsize=9, color=PAL[0], labelpad=7)
    vmax = arr.max() if arr.size else 1
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i,j]
            ax.text(j, i, str(int(v)), ha="center", va="center",
                    fontsize=12, fontweight="bold", zorder=4,
                    color="white" if v>vmax*0.58 else PAL[0])
    ax.set_title(title, fontsize=10, fontweight="bold", color=PAL[0], pad=10)
    cbar = fig.colorbar(im, ax=ax, fraction=0.038, pad=0.08)
    cbar.ax.tick_params(labelsize=8)
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=1.3)
    return fig


def _irar_fleiss_bar(kappa_val, per_cat, title="Fleiss' κ — Per-Category Agreement"):
    """Bar: overall κ + per-category — bbox labels, no overlap."""
    if not per_cat: return None
    cats = ["Overall κ"] + [str(c) for c in per_cat.keys()]
    vals = [kappa_val] + [
        float(v) if v is not None and not (isinstance(v,float) and np.isnan(v)) else np.nan
        for v in per_cat.values()]
    disp = [max(min(v,1.05),-0.22) if not np.isnan(v) else 0.0 for v in vals]
    def _col(v, i):
        if np.isnan(v): return "#cbd5e1"
        if i==0: return "#1a1a2e"
        if v>=.80: return "#16a34a"
        if v>=.60: return "#0284c7"
        if v>=.40: return "#f59e0b"
        return "#dc2626"
    fig, ax = plt.subplots(figsize=(8.5, max(3.2, 0.70*len(cats)+1.5)))
    ax.barh(cats, disp, color=[_col(vals[i],i) for i in range(len(vals))],
            edgecolor="white", height=0.50, zorder=3)
    for thr, col in [(0.20,"#94a3b8"),(0.40,"#f59e0b"),
                     (0.60,"#0284c7"),(0.80,"#16a34a")]:
        ax.axvline(thr, color=col, ls="--", lw=0.9, alpha=0.45, zorder=1)
    ax.axvline(0, color="#334155", lw=0.9, zorder=2)
    ax.set_xlim(-0.32, 1.22)
    ax.set_xlabel("Kappa (κ)", fontsize=9, color=PAL[0])
    ax.set_title(title, fontsize=10, fontweight="bold", color=PAL[0], pad=6)
    for i, (v, dv) in enumerate(zip(vals, disp)):
        if not np.isnan(v):
            lx = dv+0.04 if dv>=0 else dv-0.04
            ha = "left" if dv>=0 else "right"
            ax.text(lx, i, f"{v:.3f}", va="center", ha=ha,
                    fontsize=9, fontweight="bold", color=PAL[0], zorder=5,
                    bbox=dict(boxstyle="round,pad=0.18",fc="white",ec="none",alpha=0.90))
    ax.spines[["top","right"]].set_visible(False)
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=1.5)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# HTML EXPORT
# ══════════════════════════════════════════════════════════════════════════════

def _build_html(M, meta, figs_b, alpha):
    import base64

    def _rtbl(cols, rows, left_cols=None):
        if left_cols is None:
            left_cols = {0}
        h = '<table class="rtbl"><thead><tr>'
        for c in cols:
            h += f"<th>{c}</th>"
        h += "</tr></thead><tbody>"
        for i, row in enumerate(rows):
            h += f'<tr class="{"even" if i % 2 == 0 else "odd"}">'
            for j, cell in enumerate(row):
                cls = ' class="left"' if j in left_cols else ""
                h += f"<td{cls}>{cell}</td>"
            h += "</tr>"
        return h + "</tbody></table>"

    def _sh(t, n):
        return f'<div class="sec-hdr"><span class="sec-num">{n}</span>{t}</div>'

    def _sub(t):
        return f'<div class="sub-hdr">{t}</div>'

    def _cards(cards):
        h = '<div class="cards">'
        for lab, val, sub in cards:
            h += (f'<div class="card"><div class="card-val">{val}</div>'
                  f'<div class="card-lbl">{lab}</div>'
                  f'<div class="card-sub">{sub}</div></div>')
        return h + "</div>"

    meta_html = '<table class="meta-tbl">'
    for k, v in meta.items():
        meta_html += f'<tr><td class="mk">{k}</td><td class="mv">{v}</td></tr>'
    meta_html += "</table>"

    _mode = M.get("analysis_mode", "Internal Consistency")
    if _mode == "Inter-Rater Agreement":
        # Build per-group summary in HTML — readable cards, not one wide table
        summary_html = ""
        for _gr in M.get("constructs", []):
            _gn  = _gr.get("construct_name","—")
            _gdt = _gr.get("data_type","—").title()
            _gk  = _gr.get("k_raters",0)
            _gnu = _gr.get("n_units",0)
            _gap = ", ".join(_gr.get("applicable_methods",[]))
            summary_html += (
                f'<div class="rec-box" style="margin-bottom:10px;">'
                f'<b>{_gn}</b> | {_gdt} | {_gk} raters | {_gnu} units'
                f'<br/><small>Methods: {_gap}</small><br/>')
            # Key metrics inline
            _met = []
            _pa2 = (_gr.get("percentage_agreement") or {}).get("pa")
            if _pa2 is not None and not (isinstance(_pa2,float) and np.isnan(_pa2)):
                _met.append(f"% Agreement: {_pa2*100:.1f}%")
            _ck2 = (_gr.get("cohen_kappa") or {}).get("kappa")
            if _ck2 is not None and not (isinstance(_ck2,float) and np.isnan(_ck2)):
                _met.append(f"Cohen κ: {_ck2:.5f} ({(_gr.get('cohen_kappa') or {}).get('kappa_label','—')})")
            _ac12= (_gr.get("gwet_ac1") or {}).get("ac1")
            if _ac12 is not None and not (isinstance(_ac12,float) and np.isnan(_ac12)):
                _met.append(f"Gwet AC1: {_ac12:.5f} ({(_gr.get('gwet_ac1') or {}).get('label','—')})")
            _fk2 = (_gr.get("fleiss_kappa") or {}).get("kappa")
            if _fk2 is not None and not (isinstance(_fk2,float) and np.isnan(_fk2)):
                _met.append(f"Fleiss κ: {_fk2:.5f} ({(_gr.get('fleiss_kappa') or {}).get('kappa_label','—')})")
            _wk2 = (_gr.get("weighted_kappa") or {}).get("kappa_quadratic")
            if _wk2 is not None and not (isinstance(_wk2,float) and np.isnan(_wk2)):
                _met.append(f"Weighted κ (quad): {_wk2:.5f} ({(_gr.get('weighted_kappa') or {}).get('kappa_quadratic_label','—')})")
            _ac22= (((_gr.get("gwet_ac2") or {}).get("schemes") or {}).get("quadratic") or {}).get("ac2")
            if _ac22 is not None and not (isinstance(_ac22,float) and np.isnan(_ac22)):
                _ac2_lbl = (((_gr.get("gwet_ac2") or {}).get("schemes") or {}).get("quadratic") or {}).get("label","—")
                _met.append(f"Gwet AC2 (quadratic): {_ac22:.5f} ({_ac2_lbl})")
            _ic2 = (_gr.get("icc") or {})
            _ia12= _ic2.get("icc_2_1") if "error" not in _ic2 else None
            if _ia12 is not None and not (isinstance(_ia12,float) and np.isnan(_ia12)):
                _met.append(f"ICC(A,1): {_ia12:.5f} ({_ic2.get('icc_2_1_label','—')})")
            _cc2 = (_gr.get("lin_ccc") or {}).get("ccc")
            if _cc2 is not None and not (isinstance(_cc2,float) and np.isnan(_cc2)):
                _met.append(f"CCC: {_cc2:.5f} ({(_gr.get('lin_ccc') or {}).get('label','—')})")
            _ka2 = (_gr.get("krippendorff") or {}).get("alpha")
            if _ka2 is not None and not (isinstance(_ka2,float) and np.isnan(_ka2)):
                _met.append(f"Kripp. α: {_ka2:.5f} ({(_gr.get('krippendorff') or {}).get('label','—')})")
            summary_html += " &nbsp;|&nbsp; ".join(_met)
            summary_html += "</div>"
        summary_html += (
            '<p class="tbl-note">'
            'Benchmarks: Kappa (Landis & Koch, 1977) — &lt;0 Poor; 0.00–0.20 Slight; '
            '0.21–0.40 Fair; 0.41–0.60 Moderate; 0.61–0.80 Substantial; 0.81–1.00 Almost Perfect. '
            'ICC/CCC (Koo & Li, 2016) — &lt;0.50 Poor; 0.50–0.75 Moderate; '
            '0.75–0.90 Good; &gt;0.90 Excellent. '
            'Krippendorff (2004) — α≥0.800 reliable; 0.667≤α&lt;0.800 tentatively acceptable. '
            'See per-group sections below for full output including all methods.</p>')
        summary_title = "INTER-RATER AGREEMENT SUMMARY"
    else:
        summary_html = _rtbl(list(M["summary"].columns),
            [[_f(v) if isinstance(v,(int,float,np.floating)) else str(v)
              for v in M["summary"].loc[i]] for i in M["summary"].index])
        summary_title = "RELIABILITY SUMMARY (ALL CONSTRUCTS)"

    constructs_html = ""
    sec_n = 1
    for res in M["constructs"]:
        sec_n += 1
        name = res["construct_name"]
        body = ""
        _is_ira = M.get("analysis_mode") == "Inter-Rater Agreement"
        if _is_ira:
            irar_dtype = res.get("data_type","")
            n_u = res.get("n_units",0); k_r = res.get("k_raters",0)
            applicable = res.get("applicable_methods",[])
            method_ctx = res.get("method_context",{})

            # Group header with context
            body += (f'<div class="rec-box"><b>{res["construct_name"]}</b> | '
                     f'Data type: {irar_dtype.title()} | '
                     f'{n_u} units | {k_r} raters | '
                     f'Methods: {", ".join(applicable)}</div>')
            if method_ctx.get("guidance"):
                body += f'<p class="tbl-note">{method_ctx["guidance"]}</p>'

            def _fv2(v):
                try: return _f(v) if not np.isnan(float(v)) else "—"
                except: return "—"

            # Percentage Agreement
            pa_r = res.get("percentage_agreement") or {}
            if pa_r:
                body += _sub("Percentage Agreement (Baseline)")
                rows=[["Statistic","Value"],
                      ["Percentage Agreement",f"{pa_r.get('pa',0)*100:.2f}%"],
                      ["95% CI",_fmt_ci(pa_r.get("ci_lo",np.nan),pa_r.get("ci_hi",np.nan))],
                      ["N (units)",str(n_u)],["k (raters)",str(k_r)]]
                body += _rtbl(rows[0],rows[1:])
                body += '<p class="tbl-note">Percentage Agreement does not correct for chance. Report alongside a chance-corrected index.</p>'
                if pa_r.get("interpretation_text"):
                    body += f'<div class="interp sig">{pa_r["interpretation_text"]}</div>'
                body += f"IRAR_PA_FIG_{name}"

            # Cohen's κ
            ck = res.get("cohen_kappa") or {}
            if ck:
                body += _sub("Cohen's Kappa (κ)")
                body += (f'<p class="tbl-note">Rater 1: {ck.get("rater1","—")} | '
                         f'Rater 2: {ck.get("rater2","—")} | N: {ck.get("n",n_u)} | '
                         f'Categories: {ck.get("n_categories","—")}</p>')
                variants = ck.get("variants", {})
                scheme_rows = [["Scheme","κ","SE (null, Eq.9)","SE (general, Eq.8)","z","Sig.(2-tailed)","Interpretation"]]
                for skey, slabel in [("unweighted","Unweighted"),("linear","Linear"),("quadratic","Quadratic")]:
                    v = variants.get(skey, {})
                    scheme_rows.append([slabel, _fv2(v.get("kappa")), _fv2(v.get("se_null")),
                                         _fv2(v.get("se_general")), _fv2(v.get("z")),
                                         _p(v.get("p",np.nan)), (v.get("label","—") or "—").split(" (")[0]])
                body += "<b>Kappa Results (All Weighting Schemes)</b>"
                body += _rtbl(scheme_rows[0], scheme_rows[1:])
                body += ('<p class="tbl-note">For k=2 categories, all three schemes are mathematically '
                         'identical (only one inter-category distance is possible) — per Fleiss, J.L., '
                         '&amp; Cohen, J. (1973). Educational and Psychological Measurement, 33(3), '
                         '613–619. They diverge for 3+ ordered categories.</p>')
                body += f'<p><b>Agreement Breakdown:</b> {ck.get("agreement_breakdown_text","")}</p>'
                per_cat = ck.get("per_category", [])
                if per_cat:
                    pc_rows = [["Category","N (Rater 1)","N (Rater 2)","Agree","Pct"]]
                    for row in per_cat:
                        pc_rows.append([str(row["category"]), str(row["n_r1"]), str(row["n_r2"]),
                                         str(row["agree"]),
                                         f'{row["pct"]:.1f}%' if not np.isnan(row["pct"]) else "—"])
                    body += "<b>Per-Category Agreement</b>"
                    body += _rtbl(pc_rows[0], pc_rows[1:])
                    body += ('<p class="tbl-note">Pct = Agree / (N_Rater1 + N_Rater2 \u2212 Agree), a '
                              'Jaccard-style (intersection-over-union) same-category concordance rate.</p>')
                if ck.get("dtype") == "dichotomous":
                    body += (f'<p class="tbl-note"><b>Prevalence Index:</b> '
                              f'{_fv2(ck.get("prevalence_index",np.nan))} &nbsp;|&nbsp; '
                              f'<b>Bias Index:</b> {_fv2(ck.get("bias_index",np.nan))}</p>')
                if ck.get("kappa_ci_note"):
                    body += f'<p class="tbl-note"><b>Why no confidence interval:</b> {ck["kappa_ci_note"]}</p>'
                if ck.get("formula_reference_note"):
                    body += f'<p class="tbl-note"><b>References:</b> {ck["formula_reference_note"]}</p>'
                if ck.get("interpretation_text"): body += f'<div class="interp sig">{ck["interpretation_text"]}</div>'

            # Gwet's AC1
            ac1 = res.get("gwet_ac1") or {}
            if ac1 and ac1.get("ac1") is not None:
                body += _sub("Gwet's AC1")
                rows=[["Statistic","Value"],
                      ["Gwet's AC1",_fv2(ac1.get("ac1"))],
                      ["SE (jackknife)",_fv2(ac1.get("se"))],
                      ["z",_fv2(ac1.get("z"))],
                      ["Sig. (2-tailed)",_p(ac1.get("p",np.nan))],
                      ["95% CI (z-basis)",_fmt_ci(ac1.get("ci_lo_z",np.nan),ac1.get("ci_hi_z",np.nan))],
                      ["95% CI (t-basis, df="+str(ac1.get("ci_df","—"))+")",
                       _fmt_ci(ac1.get("ci_lo_t",np.nan),ac1.get("ci_hi_t",np.nan))],
                      ["N",str(n_u)],["k",str(k_r)],["q",str(ac1.get("q","—"))],
                      ["Interpretation",ac1.get("label","—")]]
                body += _rtbl(rows[0],rows[1:])
                if ac1.get("formula_note"): body += f'<p class="tbl-note">{ac1["formula_note"]}</p>'
                if ac1.get("dual_ci_note"): body += ac1["dual_ci_note"]
                if ac1.get("interpretation_text"): body += f'<div class="interp sig">{ac1["interpretation_text"]}</div>'

            # Scott's π
            sp = res.get("scott_pi") or {}
            if sp and not (isinstance(sp.get("pi"),float) and np.isnan(sp.get("pi",np.nan))):
                body += _sub("Scott's Pi (π)")
                rows=[["Statistic","Value"],
                      ["Scott's π",_fv2(sp.get("pi"))],
                      ["P_o",_fv2(sp.get("Po"))],["P_e (Scott)",_fv2(sp.get("Pe"))],
                      ["SE",_fv2(sp.get("se"))],["z",_fv2(sp.get("z"))],
                      ["Sig. (2-tailed)",_p(sp.get("p",np.nan))],
                      ["95% CI (z-basis)",_fmt_ci(sp.get("ci_lo_z",np.nan),sp.get("ci_hi_z",np.nan))],
                      ["95% CI (t-basis, df="+str(sp.get("ci_df","—"))+")",
                       _fmt_ci(sp.get("ci_lo_t",np.nan),sp.get("ci_hi_t",np.nan))],
                      ["N",str(n_u)],["Interpretation",sp.get("label","—")]]
                body += _rtbl(rows[0],rows[1:])
                if sp.get("dual_ci_note"): body += sp["dual_ci_note"]
                if sp.get("interpretation_text"): body += f'<div class="interp sig">{sp["interpretation_text"]}</div>'

            # Brennan-Prediger
            bp_r = res.get("brennan_prediger") or {}
            if bp_r and not (isinstance(bp_r.get("kappa_bp"),float) and np.isnan(bp_r.get("kappa_bp",np.nan))):
                body += _sub("Brennan-Prediger Coefficient (κ_BP)")
                rows=[["Statistic","Value"],
                      ["κ_BP",_fv2(bp_r.get("kappa_bp"))],
                      ["P_o",_fv2(bp_r.get("Po"))],["P_e (= 1/q)",_fv2(bp_r.get("Pe"))],
                      ["q",str(bp_r.get("q","—"))],
                      ["SE",_fv2(bp_r.get("se"))],["z",_fv2(bp_r.get("z"))],
                      ["Sig. (2-tailed)",_p(bp_r.get("p",np.nan))],
                      ["95% CI (z-basis)",_fmt_ci(bp_r.get("ci_lo_z",np.nan),bp_r.get("ci_hi_z",np.nan))],
                      ["95% CI (t-basis, df="+str(bp_r.get("ci_df","—"))+")",
                       _fmt_ci(bp_r.get("ci_lo_t",np.nan),bp_r.get("ci_hi_t",np.nan))],
                      ["N",str(n_u)],["Interpretation",bp_r.get("label","—")]]
                body += _rtbl(rows[0],rows[1:])
                if bp_r.get("dual_ci_note"): body += bp_r["dual_ci_note"]
                _bp_cmp_h = bp_r.get("comparison_table")
                if _bp_cmp_h:
                    body += '<h4 style="margin-top:1em;">Comparison with Other Coefficients</h4>'
                    _cmp_rows_h = [["Coefficient","Value","Chance-Agreement Model"]]
                    for _cn, _cv, _cd in _bp_cmp_h:
                        _cmp_rows_h.append([_cn, _fv2(_cv), _cd])
                    body += _rtbl(_cmp_rows_h[0], _cmp_rows_h[1:])
                    if bp_r.get("comparison_note"):
                        body += f'<p class="tbl-note">{bp_r["comparison_note"]}</p>'
                if bp_r.get("interpretation_text"): body += f'<div class="interp sig">{bp_r["interpretation_text"]}</div>'

            # Fleiss' κ
            fk = res.get("fleiss_kappa") or {}
            if fk:
                body += _sub("Fleiss' Kappa (κ)")
                rows=[["Statistic","Value"],
                      ["Fleiss' κ",_fv2(fk.get("kappa"))],
                      ["SE",_fv2(fk.get("kappa_se"))],["z",_fv2(fk.get("kappa_z"))],
                      ["Sig. (2-tailed)",_p(fk.get("kappa_p",np.nan))],
                      ["N",str(n_u)],["k",str(k_r)],
                      ["Interpretation",fk.get("kappa_label","—")]]
                body += _rtbl(rows[0],rows[1:])
                pc=fk.get("kappa_per_category",{})
                if pc:
                    pc_rows=[["Category","κ_j","p̂"]]
                    for cat,kv in pc.items():
                        pv=fk.get("p_per_category",{}).get(cat,np.nan)
                        pc_rows.append([str(cat),_fv2(kv),_fv2(pv)])
                    body+=_sub("Per-Category Kappa")+_rtbl(pc_rows[0],pc_rows[1:],left_cols={0})
                if fk.get("formula_note"): body += f'<p class="tbl-note">{fk["formula_note"]}</p>'
                if fk.get("interpretation_text"): body += f'<div class="interp sig">{fk["interpretation_text"]}</div>'

            # Weighted Cohen's κ
            wk = res.get("weighted_kappa") or {}
            if wk:
                body += _sub("Weighted Cohen's Kappa (κ_w)")
                rows=[["Statistic","Value","SE","z","Sig."],
                      ["κ (unweighted)",_fv2(wk.get("kappa")),_fv2(wk.get("kappa_ase")),
                       _fv2(wk.get("kappa_z")),_p(wk.get("kappa_p",np.nan))],
                      ["κ_w (linear)",_fv2(wk.get("kappa_linear")),_fv2(wk.get("kappa_linear_ase")),
                       _fv2(wk.get("kappa_linear_z")),_p(wk.get("kappa_linear_p",np.nan))],
                      ["κ_w (quadratic — primary)",_fv2(wk.get("kappa_quadratic")),
                       _fv2(wk.get("kappa_quadratic_ase")),_fv2(wk.get("kappa_quadratic_z")),
                       _p(wk.get("kappa_quadratic_p",np.nan))]]
                body += _rtbl(rows[0],rows[1:],left_cols={0})
                if wk.get("formula_note"): body += f'<p class="tbl-note">{wk["formula_note"]}</p>'
                if wk.get("interpretation_text"): body += f'<div class="interp sig">{wk["interpretation_text"]}</div>'

            # Gwet's AC2 — all five weighting schemes (parity with the Web UI)
            ac2_all = res.get("gwet_ac2") or {}
            _schemes_h = {k: v for k, v in (ac2_all.get("schemes") or {}).items()
                          if v.get("ac2") is not None and not (isinstance(v.get("ac2"), float) and np.isnan(v.get("ac2")))}
            if _schemes_h:
                body += _sub("Gwet's AC2 (Weighted) — All Five Weighting Schemes")
                for _sk in ["quadratic", "linear", "radical", "ordinal", "identity"]:
                    if _sk not in _schemes_h:
                        continue
                    ac2 = _schemes_h[_sk]
                    body += f'<h4 style="margin-top:1em;">{ac2.get("scheme_label", _sk.title())}</h4>'
                    rows=[["Statistic","Value"],
                          [f"Gwet's AC2 ({ac2.get('scheme_label','')})",_fv2(ac2.get("ac2"))],
                          ["SE (jackknife)",_fv2(ac2.get("se"))],
                          ["z",_fv2(ac2.get("z"))],
                          ["Sig. (2-tailed)",_p(ac2.get("p",np.nan))],
                          ["95% CI (z-basis)",_fmt_ci(ac2.get("ci_lo_z",np.nan),ac2.get("ci_hi_z",np.nan))],
                          ["95% CI (t-basis, df="+str(ac2.get("ci_df","—"))+")",
                           _fmt_ci(ac2.get("ci_lo_t",np.nan),ac2.get("ci_hi_t",np.nan))],
                          ["N",str(n_u)],["k",str(k_r)],["q",str(ac2.get("q","—"))],
                          ["Weight function",ac2.get("weight_formula","—")],
                          ["Interpretation",ac2.get("label","—")]]
                    body += _rtbl(rows[0],rows[1:])
                    if ac2.get("when_to_use"):
                        body += f'<p class="tbl-note"><b>When to use this scheme:</b> {ac2["when_to_use"]}</p>'
                    if ac2.get("formula_note"): body += f'<p class="tbl-note">{ac2["formula_note"]}</p>'
                    if ac2.get("dual_ci_note"): body += ac2["dual_ci_note"]
                    if ac2.get("interpretation_text"): body += f'<div class="interp sig">{ac2["interpretation_text"]}</div>'

            # ICC
            icc = res.get("icc") or {}
            if icc and "error" not in icc:
                body += _sub("Intraclass Correlation Coefficient (ICC)")
                rows=[["ICC Form","Description","ICC","95% CI","p"],
                      ["ICC(1,1)","One-way random, single rater",
                       _fv2(icc.get("icc_1_1","—")),
                       _fmt_ci(icc.get("icc_1_1_ci_lo",np.nan),icc.get("icc_1_1_ci_hi",np.nan)),
                       _fmt_p_dash(icc.get("icc_1_1_p",np.nan))],
                      ["ICC(A,1) — PRIMARY","Two-way random, absolute agreement, 1 rater",
                       _fv2(icc.get("icc_2_1")),
                       _fmt_ci(icc.get("icc_2_1_ci_lo",np.nan),icc.get("icc_2_1_ci_hi",np.nan)),
                       _fmt_p_dash(icc.get("icc_2_1_p",np.nan))],
                      ["ICC(C,1)","Two-way mixed, consistency, 1 rater",
                       _fv2(icc.get("icc_3_1")),
                       _fmt_ci(icc.get("icc_3_1_ci_lo",np.nan),icc.get("icc_3_1_ci_hi",np.nan)),
                       _fmt_p_dash(icc.get("icc_3_1_p",np.nan))],
                      ["ICC(1,k)",f"One-way random, mean of {k_r} raters",
                       _fv2(icc.get("icc_1_k","—")),
                       _fmt_ci(icc.get("icc_1_k_ci_lo",np.nan),icc.get("icc_1_k_ci_hi",np.nan)),
                       _fmt_p_dash(icc.get("icc_1_k_p",np.nan))],
                      ["ICC(A,k)",f"Two-way random, absolute agreement, mean of {k_r} raters",
                       _fv2(icc.get("icc_2_k")),
                       _fmt_ci(icc.get("icc_2_k_ci_lo",np.nan),icc.get("icc_2_k_ci_hi",np.nan)),
                       _fmt_p_dash(icc.get("icc_2_k_p",np.nan))],
                      ["ICC(C,k)",f"Two-way mixed, consistency, mean of {k_r} raters",
                       _fv2(icc.get("icc_3_k")),
                       _fmt_ci(icc.get("icc_3_k_ci_lo",np.nan),icc.get("icc_3_k_ci_hi",np.nan)),
                       _fmt_p_dash(icc.get("icc_3_k_p",np.nan))]]
                body += _rtbl(rows[0],rows[1:],left_cols={0,1})
                if icc.get("formula_note"): body += f'<p class="tbl-note">{icc["formula_note"]}</p>'
                if icc.get("interpretation_text"): body += f'<div class="interp sig">{icc["interpretation_text"]}</div>'

            # Lin's CCC
            ccc_r = res.get("lin_ccc") or {}
            if ccc_r and ccc_r.get("ccc") is not None:
                body += _sub("Lin's Concordance Correlation Coefficient (CCC)")
                rows=[["Statistic","Value","Interpretation"],
                      ["CCC (ρ_c)",_fv2(ccc_r.get("ccc")),ccc_r.get("label","—")],
                      ["Pearson r (precision)",_fv2(ccc_r.get("rho")),"Rank-order agreement"],
                      ["Bias correction C_b (accuracy)",
                       _fv2(ccc_r.get("Cb")) if not (isinstance(ccc_r.get("Cb"),float) and np.isnan(ccc_r.get("Cb",np.nan))) else "—",
                       "1.0 = no bias"],
                      ["95% CI (Fisher z)",_fmt_ci(ccc_r.get("ci_lo",np.nan),ccc_r.get("ci_hi",np.nan)),""],
                      ["N (units)",str(n_u),""]]
                body += _rtbl(rows[0],rows[1:],left_cols={0,2})
                if ccc_r.get("formula_note"): body += f'<p class="tbl-note">{ccc_r["formula_note"]}</p>'
                if ccc_r.get("interpretation_text"): body += f'<div class="interp sig">{ccc_r["interpretation_text"]}</div>'

            # Krippendorff's α
            ka = res.get("krippendorff") or {}
            if ka:
                body += _sub("Krippendorff's Alpha (α)")
                nb=ka.get("n_boot",1000)
                rows=[["Statistic","Value"],
                      ["Krippendorff's α",_fv2(ka.get("alpha"))],
                      [f"95% CI ({nb:,} bootstrap resamples)",
                       _fmt_ci(ka.get("ci_lo",np.nan),ka.get("ci_hi",np.nan))],
                      ["Data type / metric",ka.get("data_type","—").title()],
                      ["N (units)",str(n_u)],["k (raters)",str(k_r)],
                      ["Threshold — min acceptable","α ≥ 0.667 (Krippendorff, 2004)"],
                      ["Threshold — reliable","α ≥ 0.800 (Krippendorff, 2004)"],
                      ["Interpretation",ka.get("label","—")]]
                body += _rtbl(rows[0],rows[1:])
                if ka.get("formula_note"): body += f'<p class="tbl-note">{ka["formula_note"]}</p>'
                if ka.get("interpretation_text"): body += f'<div class="interp sig">{ka["interpretation_text"]}</div>'
        else:
            for blk in _coeff_blocks(res, alpha):
                body += _sub(blk["title"])
                if blk.get("sections"):
                    for sec in blk["sections"]:
                        body += f'<h4 style="margin-top:1.2em;">{sec["heading"]}</h4>'
                        if sec.get("cards"):
                            body += _cards(sec["cards"])
                        if sec.get("table"):
                            body += _rtbl(sec["table"][0], sec["table"][1],
                                          left_cols=sec.get("table_left", {0}))
                            if sec.get("table_note"):
                                body += f'<p class="tbl-note">{sec["table_note"]}</p>'
                        if sec.get("table2"):
                            body += _rtbl(sec["table2"][0], sec["table2"][1],
                                          left_cols=sec.get("table_left", {0}))
                            if sec.get("table2_note"):
                                body += f'<p class="tbl-note">{sec["table2_note"]}</p>'
                        if sec.get("interp"):
                            body += f'<div class="interp sig">{sec["interp"]}</div>'
                        if sec.get("params"):
                            body += f'<p class="tbl-note"><b>Decision parameters.</b> {sec["params"]}</p>'
                        if sec.get("note"):
                            body += f'<p class="tbl-note">{sec["note"]}</p>'
                    continue
                body += _cards(blk["cards"])
                if blk["table"]:
                    body += _rtbl(blk["table"][0], blk["table"][1],
                                  left_cols=blk.get("table_left", {0}))
                    if blk.get("table_note"):
                        body += f'<p class="tbl-note">{blk["table_note"]}</p>'
                if blk.get("table2"):
                    body += _rtbl(blk["table2"][0], blk["table2"][1],
                                  left_cols=blk.get("table_left", {0}))
                    if blk.get("table2_note"):
                        body += f'<p class="tbl-note">{blk["table2_note"]}</p>'
                if blk.get("footnote"):
                    body += f'<p class="tbl-note">{blk["footnote"]}</p>'
                body += f'<div class="interp sig">{blk["interp"]}</div>'
                body += f'<p class="tbl-note"><b>Decision parameters.</b> {blk["params"]}</p>'
                if blk["note"]:
                    body += f'<p class="tbl-note">{blk["note"]}</p>'
                if blk.get("item_diag"):
                    body += _sub("Item Diagnostics (p and p\u00d7q per item)")
                    body += _rtbl(blk["item_diag"][0], blk["item_diag"][1:],
                                  left_cols={0, 3})
                    body += ('<p class="tbl-note">p = proportion answering 1. '
                             'p\u00d7q = item variance. Items with p &lt; .10 or '
                             'p &gt; .90 cause KR-20 &gt; 1.</p>')
            # ── Internal Consistency-only sections, gated inside this
            # else branch (see the matching fix and full rationale in
            # _build_csv, found via the same audit).
            for tname, payload in _item_tables(res).items():
                body += _sub(tname)
                if tname == "Item-Total Statistics":
                    cols, rows, neg = payload
                    body += _rtbl(cols, rows, left_cols={0})
                    if neg:
                        body += ('<p class="tbl-note">a. A negative value indicates a '
                                 'negative average covariance among items, violating '
                                 'reliability model assumptions \u2014 check item codings '
                                 '(possible reverse-scored item).</p>')
                else:
                    cols, rows = payload
                    body += _rtbl(cols, rows, left_cols={0})
            scols, srows = _scale_rows(res)
            body += _sub("Scale Statistics") + _rtbl(scols, srows, left_cols={0})
            if res.get("reverse_info"):
                ritems = "; ".join(f"{it}: {f}" for it, f in res["reverse_info"])
                body += f'<p class="tbl-note">Reverse-scored items applied: {ritems}.</p>'
            elif res.get("flagged_reverse"):
                body += (f'<p class="tbl-note">Flagged possible reverse items '
                         f'(not reversed): {", ".join(res["flagged_reverse"])}.</p>')
        constructs_html += f'<div class="section">{_sh(name, sec_n)}{body}</div>'

    notes_html = ""
    for title, txt in _methodological_notes(M, alpha):
        notes_html += f'<div class="rec-box"><b>{title}.</b> {txt}</div>'

    figs_html = ""
    for fb in figs_b:
        if fb is None:
            continue
        b64 = base64.b64encode(fb).decode()
        figs_html += (f'<div class="fig-wrap"><img src="data:image/png;base64,{b64}" '
                      f'style="max-width:100%;border:1px solid #e2e8f0;border-radius:8px;"/></div>')

    # For Inter-Rater Agreement: generate per-method figures and embed in constructs_html
    if M.get("analysis_mode") == "Inter-Rater Agreement":
        # Rebuild constructs_html with embedded figures
        import io as _io
        def _fig2b64(fig):
            if fig is None: return None
            buf = _io.BytesIO(); fig.savefig(buf, format="png", dpi=110,
                                              bbox_inches="tight")
            plt.close(fig)
            return base64.b64encode(buf.getvalue()).decode()
        def _imghtml(b64):
            if b64 is None: return ""
            return (f'<div class="fig-wrap"><img src="data:image/png;base64,{b64}" '
                    f'style="max-width:100%;border:1px solid #e2e8f0;border-radius:8px;"/></div>')
        # Inject figures after each method section in constructs_html
        for _gr in M.get("constructs", []):
            _gn = _gr.get("construct_name","")
            _dtype = _gr.get("data_type","")
            _k = _gr.get("k_raters",0)
            _nu = _gr.get("n_units",0)
            # % Agreement gauge
            _pa_r = _gr.get("percentage_agreement") or {}
            if _pa_r and not (isinstance(_pa_r.get("pa"),float) and np.isnan(_pa_r.get("pa",np.nan))):
                _fg = _irar_pa_gauge(_pa_r.get("pa",np.nan),_pa_r.get("ci_lo",np.nan),
                                     _pa_r.get("ci_hi",np.nan),f"Percentage Agreement — {_gn}")
                constructs_html = constructs_html.replace(
                    f"IRAR_PA_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # Cohen's κ heatmap
            _ck_r = _gr.get("cohen_kappa") or {}
            if _ck_r and _ck_r.get("crosstab") is not None:
                _rn = _gr.get("rater_names",[])
                _fg = _irar_kappa_heatmap(_ck_r["crosstab"],
                    _rn[0] if _rn else "Rater 1",
                    _rn[1] if len(_rn)>1 else "Rater 2",
                    f"Confusion Matrix — {_gn}")
                constructs_html = constructs_html.replace(
                    f"IRAR_CK_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # Gwet's AC1
            _ac1 = _gr.get("gwet_ac1") or {}
            if _ac1 and _ac1.get("ac1") is not None:
                _fg = _irar_single_bar(_ac1.get("ac1"),_ac1.get("label","—"),"Gwet's AC1",_gn)
                constructs_html = constructs_html.replace(
                    f"IRAR_AC1_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # Fleiss κ bar
            _fk_r = _gr.get("fleiss_kappa") or {}
            if _fk_r and _fk_r.get("kappa_per_category"):
                _fg = _irar_fleiss_bar(_fk_r.get("kappa",0),
                                       _fk_r.get("kappa_per_category",{}),
                                       f"Fleiss' κ — {_gn}")
                constructs_html = constructs_html.replace(
                    f"IRAR_FK_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # Weighted κ
            _wk = _gr.get("weighted_kappa") or {}
            if _wk and _wk.get("crosstab") is not None:
                _rn = _gr.get("rater_names",[])
                _fg = _irar_kappa_heatmap(_wk["crosstab"],
                    _rn[0] if _rn else "Rater 1",
                    _rn[1] if len(_rn)>1 else "Rater 2",
                    f"Confusion Matrix (Weighted κ) — {_gn}")
                constructs_html = constructs_html.replace(
                    f"IRAR_WK_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # ICC bar
            _icc = _gr.get("icc") or {}
            if _icc and "error" not in _icc:
                _fg = _irar_icc_bar(_icc, f"ICC — {_gn}")
                constructs_html = constructs_html.replace(
                    f"IRAR_ICC_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # Krippendorff gauge
            _ka = _gr.get("krippendorff") or {}
            if _ka and not (isinstance(_ka.get("alpha"),float) and np.isnan(_ka.get("alpha",np.nan))):
                _fg = _irar_kripp_gauge(_ka.get("alpha",np.nan),_ka.get("label","—"),
                                        f"Krippendorff's α — {_gn}")
                constructs_html = constructs_html.replace(
                    f"IRAR_KA_FIG_{_gn}", _imghtml(_fig2b64(_fg)), 1)
            # CCC bar
            _ccc_r = _gr.get("lin_ccc") or {}
            if _ccc_r and _ccc_r.get("ccc") is not None:
                constructs_html = constructs_html.replace(
                    f"IRAR_CCC_FIG_{_gn}", "", 1)  # CCC has no standalone bar yet
        # Remove any unfilled placeholders
        import re as _re
        constructs_html = _re.sub(r"IRAR_[A-Z_]+_FIG_[^<]*", "", constructs_html)

    css = """<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'DM Sans',sans-serif;background:#f0f4f8;color:#1e293b;font-size:14px;line-height:1.6;}
.page{max-width:1120px;margin:0 auto;padding:32px 24px 80px;}
.cover{background:linear-gradient(135deg,#0a0a0a,#1a1a2e 50%,#16213e);border-radius:16px;padding:44px 52px;margin-bottom:28px;border-left:6px solid #e94560;box-shadow:0 12px 48px rgba(233,69,96,.2);}
.cover h1{color:#fff;font-size:2rem;font-weight:700;margin-bottom:8px;}
.cover .sub{color:#94a3b8;font-size:.9rem;margin-bottom:24px;}
.cover .badge{display:inline-block;background:#e94560;color:#fff;font-size:.7rem;padding:3px 10px;border-radius:20px;font-weight:600;margin-right:6px;}
.meta-tbl{width:100%;border-collapse:collapse;margin-top:20px;}
.meta-tbl td{padding:5px 10px;font-size:.82rem;}
.meta-tbl td.mk{color:#94a3b8;font-weight:600;width:220px;font-family:'DM Mono',monospace;}
.meta-tbl td.mv{color:#e2e8f0;}
.section{background:#fff;border-radius:12px;padding:26px 30px;margin-bottom:22px;box-shadow:0 2px 14px rgba(0,0,0,.06);}
.sec-hdr{background:linear-gradient(90deg,#1a1a2e,#16213e);color:#e2e8f0;padding:11px 20px;border-radius:8px 8px 0 0;font-weight:700;font-size:.82rem;letter-spacing:.8px;margin:-26px -30px 22px;font-family:'DM Mono',monospace;border-bottom:3px solid #e94560;display:flex;align-items:center;gap:12px;}
.sec-num{background:#e94560;color:#fff;font-size:.72rem;padding:2px 8px;border-radius:12px;font-weight:700;}
.sub-hdr{background:#f1f5f9;color:#1a1a2e;padding:8px 14px;border-radius:6px;font-weight:600;font-size:.84rem;margin:20px 0 10px;border-left:3px solid #e94560;}
.cards{display:flex;flex-wrap:wrap;gap:12px;margin:10px 0 14px;}
.card{flex:1;min-width:150px;background:linear-gradient(135deg,#fff,#f8fafc);border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.04);}
.card-val{font-size:1.5rem;font-weight:700;color:#1a1a2e;font-family:'DM Mono',monospace;}
.card-lbl{font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.6px;margin-top:4px;}
.card-sub{font-size:.72rem;color:#e94560;font-weight:600;margin-top:2px;}
.rec-box{background:linear-gradient(135deg,#f0f9ff,#e0f2fe);border-left:4px solid #0284c7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:.82rem;color:#0c4a6e;margin:12px 0;line-height:1.75;}
.rtbl{width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;font-size:.73rem;margin-bottom:6px;table-layout:fixed;word-wrap:break-word;}
.rtbl th{background:#1a1a2e;color:#e2e8f0;padding:8px 10px;text-align:center;font-weight:600;border:1px solid #334155;font-size:.71rem;}
.rtbl td{padding:6px 10px;border:1px solid #e2e8f0;text-align:right;word-wrap:break-word;}
.rtbl tr.even td{background:#fff;}.rtbl tr.odd td{background:#f8fafc;}
.rtbl td.left{text-align:left;font-weight:500;background:#f1f5f9!important;}
.tbl-note{font-size:.73rem;color:#64748b;font-style:italic;margin-top:8px;line-height:1.6;}
.interp{padding:12px 18px;border-radius:0 10px 10px 0;margin:10px 0;font-size:.86rem;line-height:1.8;border-left:4px solid #16a34a;background:linear-gradient(135deg,#f0fdf4,#dcfce7);}
.interp b{color:#16a34a;}
.fig-wrap{text-align:center;margin:18px 0;}
.footer{text-align:center;color:#94a3b8;font-size:.72rem;margin-top:44px;padding-top:16px;border-top:1px solid #e2e8f0;line-height:1.8;}
</style>"""

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Reliability Report</title>{css}</head><body><div class="page">
<div class="cover"><h1>&#129514; Reliability Analysis Report</h1>
<div class="sub"><span class="badge">Publication-Grade</span>
<span class="badge">Multi-Construct</span><span class="badge">Extended Diagnostics</span></div>
{meta_html}
<div style="margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.12);
            display:flex;align-items:center;gap:16px;">
  <div>
    <p style="color:#94a3b8;font-size:.76rem;margin:0 0 8px;">
      &#9749; Support this work &mdash; scan QRIS</p>
    <img src="https://muhaiminabdullah.com/media/images/qris_muhaiminabdullahdotcom.png"
         style="width:130px;border-radius:8px;border:2px solid #e94560;display:block;"/>
  </div>
</div></div>
<div class="section">{_sh(summary_title, 1)}{summary_html}
<p class="tbl-note">One row per construct. \u03b1 = Cronbach\u2019s alpha; \u03c9 = McDonald\u2019s omega; \u03bb2 = Guttman lambda-2; SB = Spearman-Brown split-half.</p>
{figs_html}</div>
{constructs_html}
<div class="section">{_sh("METHODOLOGICAL NOTES", len(M["constructs"])+2)}{notes_html}</div>
<div class="footer">Generated by Inferential Statistics by Muhaimin Abdullah &middot; Publication-grade statistical output<br/>
Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}</div>
</div></body></html>"""
    return html.encode("utf-8")


def _build_csv(M, meta, alpha):
    import io, csv, re
    buf = io.StringIO(); w = csv.writer(buf)
    rx = lambda s: re.sub(r"<[^>]+>", "", str(s))

    def _fv3(v):
        try: return round(float(v),3) if not (isinstance(v,float) and np.isnan(v)) else "—"
        except: return str(v) if v is not None else "—"

    w.writerow(["Reliability & Inter-Rater Agreement Report"])
    for k, v in meta.items():
        w.writerow([k, v])
    w.writerow([])

    if M.get("analysis_mode") == "Inter-Rater Agreement":
        _isum = M.get("irar_summary")
        w.writerow(["INTER-RATER AGREEMENT SUMMARY — ALL GROUPS AND METHODS"])
        if _isum is not None and not _isum.empty:
            w.writerow(list(_isum.columns))
            for idx in _isum.index:
                w.writerow([str(v) for v in _isum.loc[idx]])
        w.writerow([])
    else:
        w.writerow(["RELIABILITY SUMMARY (ALL CONSTRUCTS)"])
        w.writerow(list(M["summary"].columns))
        for idx in M["summary"].index:
            w.writerow(list(M["summary"].loc[idx]))
        w.writerow([])

    for res in M["constructs"]:
        _is_ira = M.get("analysis_mode") == "Inter-Rater Agreement"
        if _is_ira:
            irar_dtype = res.get("data_type","")
            n_u = res.get("n_units",0); k_r = res.get("k_raters",0)
            applicable = res.get("applicable_methods",[])
            w.writerow([f"GROUP: {res['construct_name']}",
                        f"Data type: {irar_dtype.title()}",
                        f"{k_r} raters", f"N = {n_u}",
                        f"Methods: {', '.join(applicable)}"])
            w.writerow([])

            # Guidance
            ctx = res.get("method_context",{})
            if ctx.get("guidance"):
                w.writerow(["Guidance", rx(ctx["guidance"])])
                w.writerow([])

            # Percentage Agreement
            pa_r = res.get("percentage_agreement") or {}
            if pa_r:
                w.writerow(["PERCENTAGE AGREEMENT (Baseline — no chance correction)"])
                w.writerow(["PA (%)", f"{pa_r.get('pa',0)*100:.2f}%",
                            "95% CI", _fmt_ci(pa_r.get("ci_lo",np.nan),pa_r.get("ci_hi",np.nan)),
                            "N", n_u, "k", k_r])
                if pa_r.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(pa_r["interpretation_text"])])
                w.writerow([])

            # Cohen's κ
            ck = res.get("cohen_kappa") or {}
            if ck:
                w.writerow(["COHEN'S KAPPA"])
                w.writerow(["Rater 1", ck.get("rater1","—"), "Rater 2", ck.get("rater2","—"),
                            "N", ck.get("n","—"), "Categories", ck.get("n_categories","—")])
                w.writerow([])
                w.writerow(["Scheme","Kappa","SE (null, Eq.9)","SE (general, Eq.8)","z","Sig.(2-tailed)","Interpretation"])
                variants = ck.get("variants", {})
                for skey, slabel in [("unweighted","Unweighted"),("linear","Linear"),("quadratic","Quadratic")]:
                    v = variants.get(skey, {})
                    w.writerow([slabel, _fv3(v.get("kappa")), _fv3(v.get("se_null")),
                                _fv3(v.get("se_general")), _fv3(v.get("z")),
                                _p(v.get("p",np.nan)), (v.get("label","—") or "—").split(" (")[0]])
                w.writerow([])
                w.writerow(["Agreement Breakdown", rx(ck.get("agreement_breakdown_text",""))])
                w.writerow([])
                per_cat = ck.get("per_category", [])
                if per_cat:
                    w.writerow(["PER-CATEGORY AGREEMENT"])
                    w.writerow(["Category","N (Rater 1)","N (Rater 2)","Agree","Pct"])
                    for row in per_cat:
                        w.writerow([row["category"], row["n_r1"], row["n_r2"], row["agree"],
                                    f'{row["pct"]:.1f}%' if not np.isnan(row["pct"]) else "—"])
                    w.writerow([])
                w.writerow(["Prevalence Index", _fv3(ck.get("prevalence_index",np.nan)),
                            "Bias Index", _fv3(ck.get("bias_index",np.nan))])
                if ck.get("kappa_ci_note"):
                    w.writerow(["Why no confidence interval", rx(ck["kappa_ci_note"])])
                if ck.get("formula_reference_note"):
                    w.writerow(["References", rx(ck["formula_reference_note"])])
                if ck.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(ck["interpretation_text"])])
                w.writerow([])

            # Gwet's AC1
            ac1 = res.get("gwet_ac1") or {}
            if ac1 and ac1.get("ac1") is not None:
                w.writerow(["GWET'S AC1"])
                w.writerow(["AC1", _fv3(ac1.get("ac1")),
                            "SE (jackknife)", _fv3(ac1.get("se")),
                            "z", _fv3(ac1.get("z")),
                            "Sig.", _p(ac1.get("p",np.nan)),
                            "95% CI (z-basis)", _fmt_ci(ac1.get("ci_lo_z",np.nan),ac1.get("ci_hi_z",np.nan)),
                            "95% CI (t-basis, df="+str(ac1.get("ci_df","—"))+")",
                            _fmt_ci(ac1.get("ci_lo_t",np.nan),ac1.get("ci_hi_t",np.nan)),
                            "q", ac1.get("q","—"),
                            "Interpretation", ac1.get("label","—")])
                if ac1.get("dual_ci_note"):
                    w.writerow(["Note (z vs t basis)", rx(ac1["dual_ci_note"])])
                if ac1.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(ac1["interpretation_text"])])
                w.writerow([])

            # Scott's π
            sp = res.get("scott_pi") or {}
            if sp and not (isinstance(sp.get("pi"),float) and np.isnan(sp.get("pi",np.nan))):
                w.writerow(["SCOTT'S PI"])
                w.writerow(["Scott's π", _fv3(sp.get("pi")),
                            "P_o", _fv3(sp.get("Po")), "P_e (Scott)", _fv3(sp.get("Pe")),
                            "SE", _fv3(sp.get("se")), "z", _fv3(sp.get("z")),
                            "Sig.", _p(sp.get("p",np.nan)),
                            "95% CI (z-basis)", _fmt_ci(sp.get("ci_lo_z",np.nan),sp.get("ci_hi_z",np.nan)),
                            "95% CI (t-basis, df="+str(sp.get("ci_df","—"))+")",
                            _fmt_ci(sp.get("ci_lo_t",np.nan),sp.get("ci_hi_t",np.nan)),
                            "Interpretation", sp.get("label","—")])
                if sp.get("dual_ci_note"):
                    w.writerow(["Note (z vs t basis)", rx(sp["dual_ci_note"])])
                if sp.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(sp["interpretation_text"])])
                w.writerow([])

            # Brennan-Prediger
            bp_r = res.get("brennan_prediger") or {}
            if bp_r and not (isinstance(bp_r.get("kappa_bp"),float) and np.isnan(bp_r.get("kappa_bp",np.nan))):
                w.writerow(["BRENNAN-PREDIGER COEFFICIENT"])
                w.writerow(["κ_BP", _fv3(bp_r.get("kappa_bp")),
                            "P_o", _fv3(bp_r.get("Po")), "P_e (1/q)", _fv3(bp_r.get("Pe")),
                            "q", bp_r.get("q","—"),
                            "SE", _fv3(bp_r.get("se")), "z", _fv3(bp_r.get("z")),
                            "Sig.", _p(bp_r.get("p",np.nan)),
                            "95% CI (z-basis)", _fmt_ci(bp_r.get("ci_lo_z",np.nan),bp_r.get("ci_hi_z",np.nan)),
                            "95% CI (t-basis, df="+str(bp_r.get("ci_df","—"))+")",
                            _fmt_ci(bp_r.get("ci_lo_t",np.nan),bp_r.get("ci_hi_t",np.nan)),
                            "Interpretation", bp_r.get("label","—")])
                if bp_r.get("dual_ci_note"):
                    w.writerow(["Note (z vs t basis)", rx(bp_r["dual_ci_note"])])
                _bp_cmp_c = bp_r.get("comparison_table")
                if _bp_cmp_c:
                    w.writerow(["-- Comparison with Other Coefficients --"])
                    w.writerow(["Coefficient","Value","Chance-Agreement Model"])
                    for _cn, _cv, _cd in _bp_cmp_c:
                        w.writerow([_cn, _fv3(_cv), rx(_cd)])
                    if bp_r.get("comparison_note"):
                        w.writerow(["Note", rx(bp_r["comparison_note"])])
                if bp_r.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(bp_r["interpretation_text"])])
                w.writerow([])

            # Fleiss' κ
            fk = res.get("fleiss_kappa") or {}
            if fk:
                w.writerow(["FLEISS' KAPPA"])
                w.writerow(["Fleiss' κ", _fv3(fk.get("kappa")),
                            "SE", _fv3(fk.get("kappa_se")), "z", _fv3(fk.get("kappa_z")),
                            "Sig.", _p(fk.get("kappa_p",np.nan)),
                            "N", n_u, "k", k_r,
                            "Interpretation", fk.get("kappa_label","—")])
                pc=fk.get("kappa_per_category",{})
                if pc:
                    w.writerow(["Per-Category κ"])
                    w.writerow(["Category","κ_j","p̂"])
                    for cat,kv in pc.items():
                        pv=fk.get("p_per_category",{}).get(cat,"")
                        w.writerow([cat,_fv3(kv),_fv3(pv)])
                if fk.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(fk["interpretation_text"])])
                w.writerow([])

            # Weighted κ
            wk = res.get("weighted_kappa") or {}
            if wk:
                w.writerow(["WEIGHTED COHEN'S KAPPA"])
                w.writerow(["κ (unweighted)", _fv3(wk.get("kappa")),
                            "SE", _fv3(wk.get("kappa_ase")), "Sig.", _p(wk.get("kappa_p",np.nan))])
                w.writerow(["κ_w (linear)", _fv3(wk.get("kappa_linear")),
                            "SE", _fv3(wk.get("kappa_linear_ase")),
                            "Sig.", _p(wk.get("kappa_linear_p",np.nan))])
                w.writerow(["κ_w (quadratic — primary)", _fv3(wk.get("kappa_quadratic")),
                            "SE", _fv3(wk.get("kappa_quadratic_ase")),
                            "Sig.", _p(wk.get("kappa_quadratic_p",np.nan)),
                            "Interpretation", wk.get("kappa_quadratic_label","—")])
                if wk.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(wk["interpretation_text"])])
                w.writerow([])

            # Gwet's AC2 — all five weighting schemes (parity with UI/HTML)
            ac2_all = res.get("gwet_ac2") or {}
            _schemes_c = {k: v for k, v in (ac2_all.get("schemes") or {}).items()
                          if v.get("ac2") is not None and not (isinstance(v.get("ac2"), float) and np.isnan(v.get("ac2")))}
            if _schemes_c:
                w.writerow(["GWET'S AC2 (WEIGHTED, ORDINAL) — ALL FIVE WEIGHTING SCHEMES"])
                for _sk in ["quadratic", "linear", "radical", "ordinal", "identity"]:
                    if _sk not in _schemes_c:
                        continue
                    ac2 = _schemes_c[_sk]
                    w.writerow([f"-- {ac2.get('scheme_label', _sk.title())} --"])
                    w.writerow([f"AC2 ({_sk})", _fv3(ac2.get("ac2")),
                                "SE (jackknife)", _fv3(ac2.get("se")),
                                "z", _fv3(ac2.get("z")),
                                "Sig.", _p(ac2.get("p",np.nan)),
                                "95% CI (z-basis)", _fmt_ci(ac2.get("ci_lo_z",np.nan),ac2.get("ci_hi_z",np.nan)),
                                "95% CI (t-basis, df="+str(ac2.get("ci_df","—"))+")",
                                _fmt_ci(ac2.get("ci_lo_t",np.nan),ac2.get("ci_hi_t",np.nan)),
                                "q", ac2.get("q","—"),
                                "Interpretation", ac2.get("label","—")])
                    if ac2.get("when_to_use"):
                        w.writerow(["When to use", rx(ac2["when_to_use"])])
                    if ac2.get("dual_ci_note"):
                        w.writerow(["Note (z vs t basis)", rx(ac2["dual_ci_note"])])
                    if ac2.get("interpretation_text"):
                        w.writerow(["Interpretation", rx(ac2["interpretation_text"])])
                    w.writerow([])

            # ICC
            icc = res.get("icc") or {}
            if icc and "error" not in icc:
                w.writerow(["INTRACLASS CORRELATION COEFFICIENT (ICC)"])
                w.writerow(["Form","Description","ICC","95% CI","p"])
                w.writerow(["ICC(1,1)","One-way random, single rater",
                            _fv3(icc.get("icc_1_1")),
                            _fmt_ci(icc.get("icc_1_1_ci_lo",np.nan),icc.get("icc_1_1_ci_hi",np.nan)),
                            _fmt_p_dash(icc.get("icc_1_1_p",np.nan))])
                w.writerow(["ICC(A,1) — PRIMARY","Two-way random, absolute, single rater",
                            _fv3(icc.get("icc_2_1")),
                            _fmt_ci(icc.get("icc_2_1_ci_lo",np.nan),icc.get("icc_2_1_ci_hi",np.nan)),
                            _fmt_p_dash(icc.get("icc_2_1_p",np.nan))])
                w.writerow(["ICC(C,1)","Two-way mixed, consistency, single rater",
                            _fv3(icc.get("icc_3_1")),
                            _fmt_ci(icc.get("icc_3_1_ci_lo",np.nan),icc.get("icc_3_1_ci_hi",np.nan)),
                            _fmt_p_dash(icc.get("icc_3_1_p",np.nan))])
                w.writerow(["ICC(1,k)","One-way random, mean of k raters",
                            _fv3(icc.get("icc_1_k")),
                            _fmt_ci(icc.get("icc_1_k_ci_lo",np.nan),icc.get("icc_1_k_ci_hi",np.nan)),
                            _fmt_p_dash(icc.get("icc_1_k_p",np.nan))])
                w.writerow(["ICC(A,k)","Two-way random, absolute, mean of k raters",
                            _fv3(icc.get("icc_2_k")),
                            _fmt_ci(icc.get("icc_2_k_ci_lo",np.nan),icc.get("icc_2_k_ci_hi",np.nan)),
                            _fmt_p_dash(icc.get("icc_2_k_p",np.nan))])
                w.writerow(["ICC(C,k)","Two-way mixed, consistency, mean of k raters",
                            _fv3(icc.get("icc_3_k")),
                            _fmt_ci(icc.get("icc_3_k_ci_lo",np.nan),icc.get("icc_3_k_ci_hi",np.nan)),
                            _fmt_p_dash(icc.get("icc_3_k_p",np.nan))])
                if icc.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(icc["interpretation_text"])])
                w.writerow([])

            # Lin's CCC
            ccc_r = res.get("lin_ccc") or {}
            if ccc_r and ccc_r.get("ccc") is not None:
                w.writerow(["LIN'S CONCORDANCE CORRELATION COEFFICIENT (CCC)"])
                w.writerow(["CCC (ρ_c)", _fv3(ccc_r.get("ccc")),
                            "Pearson r (precision)", _fv3(ccc_r.get("rho")),
                            "C_b (accuracy)", _fv3(ccc_r.get("Cb")) if not (isinstance(ccc_r.get("Cb"),float) and np.isnan(ccc_r.get("Cb",np.nan))) else "—",
                            "95% CI", _fmt_ci(ccc_r.get("ci_lo",np.nan),ccc_r.get("ci_hi",np.nan)),
                            "N", n_u, "Interpretation", ccc_r.get("label","—")])
                if ccc_r.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(ccc_r["interpretation_text"])])
                w.writerow([])

            # Krippendorff's α
            ka = res.get("krippendorff") or {}
            if ka:
                nb=ka.get("n_boot",1000)
                w.writerow(["KRIPPENDORFF'S ALPHA"])
                w.writerow(["Krippendorff's α", _fv3(ka.get("alpha")),
                            f"95% CI ({nb} resamples)",
                            _fmt_ci(ka.get("ci_lo",np.nan),ka.get("ci_hi",np.nan)),
                            "Data type", ka.get("data_type","—").title(),
                            "N", n_u, "k", k_r,
                            "Interpretation", ka.get("label","—")])
                if ka.get("interpretation_text"):
                    w.writerow(["Interpretation", rx(ka["interpretation_text"])])
                w.writerow([])

            w.writerow(["---"])
            w.writerow([])
        else:
            for blk in _coeff_blocks(res, alpha):
                w.writerow([f"[{blk['title']}]"])
                if blk.get("sections"):
                    for sec in blk["sections"]:
                        w.writerow([f"-- {sec['heading']} --"])
                        if sec.get("table"):
                            w.writerow(sec["table"][0])
                            for r in sec["table"][1]:
                                w.writerow(r)
                            if sec.get("table_note"):
                                w.writerow([rx(sec["table_note"])])
                        if sec.get("table2"):
                            w.writerow(sec["table2"][0])
                            for r in sec["table2"][1]:
                                w.writerow(r)
                            if sec.get("table2_note"):
                                w.writerow([rx(sec["table2_note"])])
                        if sec.get("interp"):
                            w.writerow(["Interpretation", rx(sec["interp"])])
                        if sec.get("params"):
                            w.writerow(["Decision parameters", rx(sec["params"])])
                        if sec.get("note"):
                            w.writerow(["Note", rx(sec["note"])])
                        w.writerow([])
                    w.writerow(["---"])
                    w.writerow([])
                    continue
                if blk["table"]:
                    w.writerow(blk["table"][0])
                    for r in blk["table"][1]:
                        w.writerow(r)
                    if blk.get("table_note"):
                        w.writerow([rx(blk["table_note"])])
                if blk.get("table2"):
                    w.writerow(blk["table2"][0])
                    for r in blk["table2"][1]:
                        w.writerow(r)
                    if blk.get("table2_note"):
                        w.writerow([rx(blk["table2_note"])])
                if blk.get("footnote"):
                    w.writerow([rx(blk["footnote"])])
                w.writerow(["Interpretation", rx(blk["interp"])])
                w.writerow(["Decision parameters", rx(blk["params"])])
                if blk["note"]:
                    w.writerow(["Note", rx(blk["note"])])
                if blk.get("item_diag"):
                    w.writerow(["Item Diagnostics (p and p\u00d7q per item)"])
                    w.writerow(blk["item_diag"][0])
                    for _dr in blk["item_diag"][1:]:
                        w.writerow(_dr)
                w.writerow([])
            # ── Internal Consistency-only sections (item tables, scale
            # statistics, reverse-scoring info) -- gated inside this
            # else branch. Previously these ran UNCONDITIONALLY for
            # every construct regardless of analysis_mode: _item_tables()
            # is internally guarded and produced empty output for
            # Inter-Rater Agreement data (wasted computation only), but
            # _scale_rows() is NOT internally guarded and unconditionally
            # emitted a full "SCALE STATISTICS" section (11 rows of "."
            # placeholders) into every Inter-Rater Agreement CSV export --
            # visible clutter in the user's downloaded file, not merely
            # wasted computation. Found via direct code audit.
            for tname, payload in _item_tables(res).items():
                w.writerow([tname.upper()])
                if tname == "Item-Total Statistics":
                    cols, rows, neg = payload
                    w.writerow(cols)
                    for r in rows:
                        w.writerow(r)
                    if neg:
                        w.writerow(["a. Negative value violates reliability model "
                                    "assumptions; check item codings."])
                else:
                    cols, rows = payload
                    w.writerow(cols)
                    for r in rows:
                        w.writerow(r)
                w.writerow([])
            scols, srows = _scale_rows(res)
            w.writerow(["SCALE STATISTICS"])
            w.writerow(scols)
            for r in srows:
                w.writerow(r)
            if res.get("reverse_info"):
                w.writerow(["Reverse-scored items applied",
                            "; ".join(f"{it}: {f}" for it, f in res["reverse_info"])])
            elif res.get("flagged_reverse"):
                w.writerow(["Flagged possible reverse items (not reversed)",
                            ", ".join(res["flagged_reverse"])])
        w.writerow([])
    w.writerow(["METHODOLOGICAL NOTES"])
    for title, txt in _methodological_notes(M, alpha):
        w.writerow([title, rx(txt)])
    return buf.getvalue().encode("utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# CSS + HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(load_page_css(), unsafe_allow_html=True)

st.markdown("""
<div class="main-hdr">
  <h1>&#129514; Reliability Analysis
    <span class="badge">Publication-Grade</span>
    <span class="badge">Multi-Construct</span>
    <span class="badge">Extended Diagnostics</span>
  </h1>
  <p>Cronbach&#39;s &alpha; &middot; KR-20 &middot; Split-half &middot;
     Guttman &lambda; &middot; ICC &middot; McDonald&#39;s &omega; &nbsp;&middot;&nbsp;
     Analyse multiple constructs from a single file in one run</p>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom:1rem;">
  <p style="color:#64748b;font-size:.9rem;margin-bottom:.4rem;">
    &#9749; Support this work &mdash; scan QRIS:</p>
  <img src="https://muhaiminabdullah.com/media/images/qris_muhaiminabdullahdotcom.png"
       style="width:180px;border-radius:10px;border:2px solid #e94560;display:block;"/>
</div>""", unsafe_allow_html=True)

st.info(
    "\u2139\ufe0f The first row of your file is treated as the header "
    "(variable names) and is never counted as data. "
    "**Internal Consistency**: upload one file containing all items, "
    "choose how many constructs you have, then assign items to each. "
    "**Inter-Rater Agreement**: each column should represent one rater/judge, "
    "each row one unit being rated.")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### &#9881;&#65039; Configuration")
    st.markdown("---")
    alpha = st.selectbox("\u03b1 (for confidence intervals)",
                         [0.05, 0.01, 0.10], index=0)
    analysis_mode = st.radio(
        "&#128202; Analysis Mode",
        ["Internal Consistency", "Inter-Rater Agreement"],
        index=0,
        help=("**Internal Consistency**: Cronbach \u03b1, KR-20, Omega, "
              "Split-half, Guttman \u03bb, ICC(C). "
              "Columns = scale items measured per respondent.\n\n"
              "**Inter-Rater Agreement**: Cohen\u2019s \u03ba (2 raters) or "
              "Fleiss\u2019 \u03ba (\u22653 raters) + ICC(A). "
              "Columns = raters, rows = units being rated."))
    st.markdown("---")

    # ── Sample data ───────────────────────────────────────────────────────────
    if analysis_mode == "Inter-Rater Agreement":
        irar_sample_map = {
            "Dichotomous — 2 raters":   "IRAR Dichotomous",
            "Nominal — 3 raters":        "IRAR Nominal",
            "Ordinal — 2 raters":        "IRAR Ordinal",
            "Ordinal — 3 raters":        "IRAR Ordinal Multi",
            "Interval — 4 raters":       "IRAR Interval",
            "Interval — 2 raters (CCC)": "IRAR Interval 2-rater",
        }
        with st.expander("📂 Sample Datasets"):
            samp_choice = st.selectbox(
                "Configuration",
                list(irar_sample_map.keys()),
                key="irar_samp_sel",
                help="Each file demonstrates a distinct data type and rater count.")
            samp_key = irar_sample_map[samp_choice]
            samp = SAMPLES.get(samp_key)
            if samp:
                st.caption(samp.get("note",""))
                fname = f"sample_{samp_key.lower().replace(' ','_')}.csv"
                st.download_button(
                    "⬇️ Download CSV", samp["csv"].encode(),
                    fname, "text/csv", use_container_width=True)
    else:
        samp_key = "Reliability Analysis"
        samp = SAMPLES.get(samp_key)
        if samp:
            with st.expander("📂 Sample Dataset"):
                st.caption(samp.get("note",""))
                st.download_button(
                    "⬇️ Download Sample CSV", samp["csv"].encode(),
                    "sample_reliability.csv", "text/csv",
                    use_container_width=True)
    st.markdown("---")

    uploaded = st.file_uploader("&#128194; Upload Data File",
                                type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            df = load_file(uploaded)
            fm = file_metadata(uploaded, df)
            val = validate_file(df)
            if val["errors"]:
                for e in val["errors"]: st.error(e)
                df = None
            else:
                st.success(f"&#10003; {fm['Rows']:,} rows \u00d7 {fm['Columns']} cols")
                for wm in val["warnings"]: st.warning(wm)
        except Exception as e:
            st.error(str(e)); df = None
    elif samp is not None:
        df = load_from_string(samp["csv"])
        st.info("\u2139\ufe0f Using built-in sample data")
    else:
        df = None

    cfg = None
    if df is not None:
        num_cols = get_numeric_cols(df)

        def _is_id(col, series):
            cl = col.lower().strip()
            idn = {'id', 'no', 'num', 'number', 'index', 'subject_id',
                   'respondent', 'participant', 'sampel', 'nomor'}
            if not (cl in idn or cl.endswith(('_id', '_no'))
                    or cl.startswith(('id_', 'subject'))):
                return False
            s = series.dropna()
            try:
                return bool((s == s.astype(int)).all()) and s.nunique() == len(s)
            except Exception:
                return False
        avail = [c for c in num_cols if not _is_id(c, df[c])]

        st.markdown("---")

        if analysis_mode == "Inter-Rater Agreement":
            st.info(
                "📋 **Data format:** Each **column** = one rater. "
                "Each **row** = one unit rated (student, essay, item). "
                "All raters must score the same set of units.")

            n_groups = st.number_input(
                "Number of rating groups",
                min_value=1, max_value=20, value=1, step=1,
                help="Each group = one set of raters rating the same units on one aspect.")

            dtype_options = {
                "Dichotomous (0/1, Yes/No, Pass/Fail)":           "dichotomous",
                "Nominal (A/B/C, error type, unordered)":          "nominal",
                "Ordinal (Likert 1–5, rubric 1–4, ordered)":       "ordinal",
                "Interval (scores 0–100, continuous)":             "interval",
                "Ratio (time, weight, continuous with true zero)":  "ratio",
            }

            constructs = []; used_globally = []
            kripp_will_run = False  # track if any group needs Krippendorff
            scale_declarations_ok = True  # tracks whether every group that
            # needs a declared instrument scale (AC1/AC2/Brennan-Prediger)
            # has actually supplied it -- gates the Run button below.
            for i in range(int(n_groups)):
                st.markdown(f"**Rating Group {i+1}**")
                # Fix [11]: separate widget keys for IRAR vs IC (irar_ prefix)
                cname = st.text_input(
                    "Group name", value=f"Rating Group {i+1}",
                    key=f"irar_name_{i}")
                avail_now = [c for c in avail if c not in used_globally]
                citems = st.multiselect(
                    "Select rater columns (≥ 2)",
                    avail_now, key=f"irar_items_{i}",
                    help="Each column = one rater. Columns used in other groups are excluded.")
                dtype_choice = st.selectbox(
                    "Data type",
                    list(dtype_options.keys()),
                    key=f"irar_dtype_{i}",
                    help=(
                        "Dichotomous: exactly 2 categories (0/1, Yes/No).\n"
                        "Nominal: 3+ unordered categories (error type, A/B/C).\n"
                        "Ordinal: ordered levels (Likert scale, rubric).\n"
                        "Interval: continuous scores without true zero.\n"
                        "Ratio: continuous with true zero (time, frequency)."))
                irar_dtype_i = dtype_options[dtype_choice]
                q_declared_i = None; scale_min_i = None
                if citems:
                    k = len(citems)
                    from modules.reliability import _get_applicable_methods
                    methods = _get_applicable_methods(irar_dtype_i, k)
                    if "krippendorff" in methods:
                        kripp_will_run = True
                    method_names = {
                        "pct":          "% Agreement",
                        "cohen":        "Cohen's κ",
                        "gwet_ac1":     "Gwet's AC1",
                        "scott_pi":     "Scott's π",
                        "bp":           "Brennan-Prediger",
                        "fleiss":       "Fleiss' κ",
                        "weighted":     "Weighted Cohen's κ",
                        "gwet_ac2":     "Gwet's AC2",
                        "icc":          "ICC (all 6 forms)",
                        "ccc":          "Lin's CCC",
                        "krippendorff": "Krippendorff's α",
                    }
                    methods_str = " + ".join(method_names.get(m, m) for m in methods)
                    st.markdown(
                        f'<div style="font-size:.78rem;color:#0284c7;'
                        f'padding:4px 8px;background:#f0f9ff;border-radius:4px;">'
                        f'&#10003; {k} rater{"s" if k>1 else ""} | '
                        f'{irar_dtype_i.title()} → '
                        f'<b>{methods_str}</b>'
                        f'</div>', unsafe_allow_html=True)

                    # ── Mandatory instrument-scale declaration ────────────
                    # Required (not optional, not defaulted, not inferred)
                    # whenever a q-dependent coefficient is applicable for
                    # this group: Gwet's AC1, Gwet's AC2, or Brennan-
                    # Prediger. Per the primary-theory audit (Gwet,
                    # Handbook of Inter-Rater Reliability, Ch. 5; Brennan
                    # & Prediger, 1981), q must reflect the instrument's
                    # declared category count -- a fact the application
                    # cannot infer or guess from the data alone, since a
                    # valid category may simply be absent from a given
                    # sample. Fields start EMPTY (no plausible-looking
                    # default) and the Run button is disabled until every
                    # such group has a value.
                    needs_q = any(m in methods for m in ("gwet_ac1", "bp"))
                    needs_ac2 = "gwet_ac2" in methods
                    if needs_q or needs_ac2:
                        st.markdown(
                            '<p style="font-size:.78rem;color:#9a3412;'
                            'font-weight:600;margin:6px 0 2px;">'
                            '&#9888; Required: declare the full instrument scale '
                            '(not just the values observed in this data) — see '
                            'Gwet (2014) / Brennan &amp; Prediger (1981).</p>',
                            unsafe_allow_html=True)
                    if needs_ac2 and irar_dtype_i == "ordinal":
                        sc1, sc2 = st.columns(2)
                        smin_in = sc1.number_input(
                            "Scale minimum", value=None, step=1.0,
                            key=f"irar_scalemin_{i}", placeholder="e.g., 1",
                            help="The lowest possible value on the rating instrument, "
                                 "whether or not it was actually used by raters.")
                        smax_in = sc2.number_input(
                            "Scale maximum", value=None, step=1.0,
                            key=f"irar_scalemax_{i}", placeholder="e.g., 5",
                            help="The highest possible value on the rating instrument, "
                                 "whether or not it was actually used by raters.")
                        if smin_in is not None and smax_in is not None and smax_in > smin_in:
                            q_declared_i = int(smax_in - smin_in + 1)
                            scale_min_i = int(smin_in)
                            st.caption(f"Declared scale: {int(smin_in)}–{int(smax_in)} "
                                       f"→ q = {q_declared_i} categories. Gwet's AC2 will "
                                       f"be computed under all five standard weighting "
                                       f"schemes (see the AC2 tab for the full set).")
                        else:
                            scale_declarations_ok = False
                            st.error("Enter both scale minimum and maximum "
                                     "(maximum must exceed minimum) to proceed.")
                    elif needs_q and not needs_ac2:
                        # Dichotomous/nominal: no inherent order, so a bare
                        # category count is requested rather than min/max.
                        q_in = st.number_input(
                            "Total number of categories in the coding scheme",
                            value=None, step=1, min_value=2,
                            key=f"irar_qcount_{i}", placeholder="e.g., 5",
                            help="The number of categories the coding scheme "
                                 "defines, whether or not every category was "
                                 "actually used by raters in this dataset.")
                        if q_in is not None:
                            q_declared_i = int(q_in)
                        else:
                            scale_declarations_ok = False
                            st.error("Enter the total number of categories to proceed.")

                    constructs.append({
                        "name": cname, "items": citems,
                        "data_type": irar_dtype_i,
                        "q_declared": q_declared_i,
                        "scale_min": scale_min_i})
                    used_globally.extend(citems)
                st.markdown("")

            # Fix [7]: Bootstrap option — shown only when Krippendorff will run
            n_boot_irar = 200
            if kripp_will_run:
                st.markdown("---")
                st.markdown("**Krippendorff's α — Bootstrap CI**")
                _boot_opts = {
                    "200 resamples (fast, ~1–3 s)":   200,
                    "400 resamples (moderate, ~2–6 s)": 400,
                    "600 resamples (slower)":           600,
                    "1,000 resamples (may be slow for ordinal/ratio data)": 1000,
                }
                _boot_choice = st.selectbox(
                    "Bootstrap resamples for 95% CI",
                    list(_boot_opts.keys()),
                    index=0,
                    key="irar_n_boot",
                    help=(
                        "Larger values give more stable CI estimates but increase "
                        "computation time. For ordinal or ratio data with many "
                        "observations, keep ≤ 400 to avoid long runtimes."))
                n_boot_irar = _boot_opts[_boot_choice]
                # Warn for ordinal/ratio + large n_boot
                _ordinal_ratio = any(
                    c.get("data_type") in ("ordinal","ratio")
                    for c in constructs)
                if _ordinal_ratio and n_boot_irar > 400:
                    st.warning(
                        "⚠️ Ordinal or ratio data selected with "
                        f"{n_boot_irar:,} bootstrap resamples. "
                        "This may take considerably longer. "
                        "Consider 200–400 resamples for faster results.")

            auto_rev = False; rev_method = "theoretical"; smin = smax = None

        else:
            # ── Internal Consistency: original UI ────────────────────────
            scale_declarations_ok = True  # not applicable to IC; default safe
            n_constructs = st.number_input(
                "\U0001f4ca Number of constructs",
                min_value=1, max_value=20, value=1, step=1)
            constructs = []; used = []
            for i in range(int(n_constructs)):
                st.markdown(f"**Construct {i+1}**")
                cname = st.text_input(
                    "Name", value=f"Construct {i+1}", key=f"rel_name_{i}")
                citems = st.multiselect(
                    "Items (\u2265 2)", avail, key=f"rel_items_{i}")
                if citems:
                    constructs.append({"name": cname, "items": citems})
                    used.extend(citems)
            dupes = set([x for x in used if used.count(x) > 1])
            if dupes:
                st.warning(
                    f"\u26a0\ufe0f Items in multiple constructs: {', '.join(dupes)}")

            st.markdown("---")
            st.markdown("**\U0001f504 Reverse-Item Handling**")
            auto_rev = st.checkbox(
                "Auto-reverse flagged items", value=False,
                help="Off by default. When on, items with a negative "
                     "item-total correlation are reversed.")
            rev_method = "theoretical"; smin = smax = None
            if auto_rev:
                rev_method = st.selectbox(
                    "Reversal method",
                    ["theoretical", "observed", "zscore"], index=0)
                if rev_method == "theoretical":
                    c1, c2 = st.columns(2)
                    smin = c1.number_input("Scale min", value=1.0)
                    smax = c2.number_input("Scale max", value=5.0)

            st.markdown("---")
            st.markdown("**\U0001f4c8 Additional Analyses (Optional)**")
            compute_bootstrap_ci = st.checkbox(
                "Compute bootstrap confidence intervals",
                value=False,
                help="Adds 95% percentile-bootstrap confidence intervals for "
                     "Guttman's Lambda (all 6 forms, both bases), all three "
                     "Split-Half variants, and McDonald's Omega-u (both "
                     "bases) \u2014 following the method recommended by "
                     "Kelley & Pornprasertmanit (2016) for reliability "
                     "coefficients generally. Off by default: adds "
                     "meaningfully to computation time (typically a few "
                     "seconds to under a minute, depending on item count) "
                     "since it involves ~15 separate bootstrap runs.")
            compute_omega_h = st.checkbox(
                "Compute McDonald's Omega-Hierarchical (\u03c9h)",
                value=False,
                help="Off by default. Investigation found this coefficient's "
                     "oblique-rotation extraction can take substantial, "
                     "unpredictable time (milliseconds to 10+ seconds) for "
                     "certain data structures, independent of item count \u2014 "
                     "this protects the speed of every other coefficient, "
                     "none of which share this issue. A confidence interval "
                     "is not computed for \u03c9h even when enabled (see the "
                     "\u03c9h section for the disclosed reason).")

        valid = [c for c in constructs if len(c.get("items",[])) >= 2]
        if len(valid) < len(constructs):
            _unit = "rater groups" if analysis_mode == "Inter-Rater Agreement" else "constructs"
            _min  = "raters"       if analysis_mode == "Inter-Rater Agreement" else "items"
            st.warning(f"Each {_unit[:-1]} needs at least 2 {_min}.")
        if valid:
            cfg = {"constructs": valid, "auto_rev": auto_rev,
                   "rev_method": rev_method, "smin": smin, "smax": smax,
                   "analysis_mode": analysis_mode,
                   "n_boot": n_boot_irar if analysis_mode == "Inter-Rater Agreement" else 200,
                   "compute_bootstrap_ci": compute_bootstrap_ci if analysis_mode == "Internal Consistency" else False,
                   "compute_omega_h": compute_omega_h if analysis_mode == "Internal Consistency" else False}
        st.markdown("---")
        if not scale_declarations_ok:
            st.info("&#128274; Complete every required instrument-scale field "
                     "above (marked with &#9888;) to enable analysis.")
        run_btn = st.button("&#128640; Run Analysis", type="primary",
                            use_container_width=True,
                            disabled=not scale_declarations_ok)
    else:
        run_btn = False

# ── Data preview ─────────────────────────────────────────────────────────────
if df is not None:
    with st.expander("&#128269; Data Preview (row 1 = header, not data)", expanded=False):
        st.dataframe(df.head(20), use_container_width=True)

# ── Welcome ──────────────────────────────────────────────────────────────────
if not run_btn and "rel_M" not in st.session_state:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#f0f9ff,#e0f2fe);'
        'border:1px solid #bae6fd;border-radius:12px;padding:1.2rem 1.4rem;'
        'margin:.8rem 0;border-left:4px solid #0284c7;">'
        '<h4 style="margin:0 0 .4rem;font-size:.95rem;font-weight:700;">'
        '&#129514; Reliability Analysis</h4>'
        '<p style="margin:0;font-size:.84rem;color:#475569;">'
        'Upload one file and choose <b>Internal Consistency</b> '
        '(Cronbach \u03b1, KR-20, Omega, ICC) or <b>Inter-Rater Agreement</b> '
        '(Cohen\u2019s \u03ba, Fleiss\u2019 \u03ba, ICC). '
        'For Internal Consistency: assign columns to constructs. '
        'For Inter-Rater: each column = one rater, each row = one unit rated.'
        '</p></div>',
        unsafe_allow_html=True)
    st.info("&#128072; Configure constructs in the sidebar, then click **Run Analysis**.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:
    if cfg is None:
        st.error("&#9888;&#65039; Define at least one group/construct with \u2265 2 items/raters.")
        st.stop()
    with st.spinner("Computing analysis\u2026"):
        try:
            if cfg["analysis_mode"] == "Inter-Rater Agreement":
                from modules.reliability import run_multi_irar
                M = run_multi_irar(df, cfg["constructs"], alpha=alpha,
                                   n_boot=cfg.get("n_boot", 200))
                M["analysis_mode"] = "Inter-Rater Agreement"
                meta = {
                    "Analysis":  "Inter-Rater Agreement",
                    "Groups":    len(M["constructs"]),
                    "\u03b1":    alpha,
                    "Date":      datetime.now().strftime("%B %d, %Y %H:%M"),
                }
                figs_b = [None]  # No summary bar chart — visuals are inside each method tab

            else:
                # ── Internal Consistency ──────────────────────────────────
                M = run_multi_reliability(
                    df, cfg["constructs"], alpha=alpha,
                    reverse_method=cfg["rev_method"], auto_reverse=cfg["auto_rev"],
                    scale_min=cfg["smin"], scale_max=cfg["smax"],
                    compute_bootstrap_ci=cfg.get("compute_bootstrap_ci", False),
                    compute_omega_h=cfg.get("compute_omega_h", False))
                M["reverse_method"] = cfg["rev_method"] if cfg["auto_rev"] else None
                M["analysis_mode"]  = "Internal Consistency"
                meta = {
                    "Analysis":   "Internal Consistency",
                    "Constructs": len(M["constructs"]),
                    "\u03b1 (CI level)": alpha,
                    "Date":       datetime.now().strftime("%B %d, %Y %H:%M"),
                }
                figs_b = [fig_to_bytes(_alpha_bar(M["summary"]))]
                for res in M["constructs"]:
                    f = _item_total_plot(res)
                    figs_b.append(fig_to_bytes(f) if f is not None else None)

        except Exception as e:
            import traceback as _tb
            st.error(f"&#9888;&#65039; Analysis could not be completed: {e}")
            st.code(_tb.format_exc()); st.stop()

    st.session_state.update({"rel_M": M, "rel_meta": meta,
                             "rel_figs": figs_b, "rel_alpha": alpha,
                             "rel_mode": cfg["analysis_mode"]})

# ══════════════════════════════════════════════════════════════════════════════
# LOAD FROM SESSION
# ══════════════════════════════════════════════════════════════════════════════
M        = st.session_state["rel_M"]
meta     = st.session_state["rel_meta"]
figs_b   = st.session_state["rel_figs"]
alpha    = st.session_state.get("rel_alpha", 0.05)
rel_mode = st.session_state.get("rel_mode", "Internal Consistency")

st.success("&#10003; Analysis complete!")

if rel_mode == "Inter-Rater Agreement":
    # ── Comprehensive Inter-Rater Summary (Issue 6) ───────────────────────
    st.markdown('<div class="sec-title">Inter-Rater Agreement Summary — All Groups</div>',
                unsafe_allow_html=True)

    # Redesigned summary: per-group metric cards, not one wide table
    for _grp_res in M.get("constructs",[]):
        _gname   = _grp_res.get("construct_name","—")
        _gdtype  = _grp_res.get("data_type","—").title()
        _gnunits = _grp_res.get("n_units",0)
        _gk      = _grp_res.get("k_raters",0)
        _gappl   = _grp_res.get("applicable_methods",[])

        st.markdown(
            f'<div style="background:#f8fafc;border:1px solid #e2e8f0;'
            f'border-radius:8px;padding:14px 18px;margin-bottom:12px;">'
            f'<div style="font-size:.95rem;font-weight:700;color:#1a1a2e;'
            f'margin-bottom:8px;">&#128202; {_gname}</div>'
            f'<div style="font-size:.78rem;color:#64748b;margin-bottom:10px;">'
            f'Data type: <b>{_gdtype}</b> &nbsp;|&nbsp; '
            f'{_gk} raters &nbsp;|&nbsp; {_gnunits} units &nbsp;|&nbsp; '
            f'Methods: {", ".join(_gappl)}</div>',
            unsafe_allow_html=True)

        # Build metric pairs for applicable methods
        _metrics = []
        _pa = (_grp_res.get("percentage_agreement") or {}).get("pa")
        if _pa is not None and not (isinstance(_pa,float) and np.isnan(_pa)):
            _metrics.append(("% Agreement", f"{_pa*100:.1f}%", "baseline"))

        _ck = (_grp_res.get("cohen_kappa") or {}).get("kappa")
        if _ck is not None and not (isinstance(_ck,float) and np.isnan(_ck)):
            _ck_lbl = (_grp_res.get("cohen_kappa") or {}).get("kappa_label","—")
            _metrics.append(("Cohen's κ", f"{_ck:.5f}", _ck_lbl))

        _ac1 = (_grp_res.get("gwet_ac1") or {}).get("ac1")
        if _ac1 is not None and not (isinstance(_ac1,float) and np.isnan(_ac1)):
            _ac1_lbl = (_grp_res.get("gwet_ac1") or {}).get("label","—")
            _metrics.append(("Gwet's AC1", f"{_ac1:.5f}", _ac1_lbl))

        _sp = (_grp_res.get("scott_pi") or {}).get("pi")
        if _sp is not None and not (isinstance(_sp,float) and np.isnan(_sp)):
            _metrics.append(("Scott's π", f"{_sp:.5f}",
                             (_grp_res.get("scott_pi") or {}).get("label","—")))

        _bp2 = (_grp_res.get("brennan_prediger") or {}).get("kappa_bp")
        if _bp2 is not None and not (isinstance(_bp2,float) and np.isnan(_bp2)):
            _metrics.append(("Brennan-Prediger", f"{_bp2:.5f}",
                             (_grp_res.get("brennan_prediger") or {}).get("label","—")))

        _fk = (_grp_res.get("fleiss_kappa") or {}).get("kappa")
        if _fk is not None and not (isinstance(_fk,float) and np.isnan(_fk)):
            _metrics.append(("Fleiss' κ", f"{_fk:.5f}",
                             (_grp_res.get("fleiss_kappa") or {}).get("kappa_label","—")))

        _wkq = (_grp_res.get("weighted_kappa") or {}).get("kappa_quadratic")
        if _wkq is not None and not (isinstance(_wkq,float) and np.isnan(_wkq)):
            _metrics.append(("Weighted κ (quad)", f"{_wkq:.5f}",
                             (_grp_res.get("weighted_kappa") or {}).get("kappa_quadratic_label","—")))

        _ac2_quad = ((_grp_res.get("gwet_ac2") or {}).get("schemes") or {}).get("quadratic") or {}
        _ac2 = _ac2_quad.get("ac2")
        if _ac2 is not None and not (isinstance(_ac2,float) and np.isnan(_ac2)):
            _metrics.append(("Gwet's AC2 (quadratic)", f"{_ac2:.5f}",
                             _ac2_quad.get("label","—")))

        _icc_r = _grp_res.get("icc") or {}
        _ia1 = _icc_r.get("icc_2_1") if "error" not in _icc_r else None
        if _ia1 is not None and not (isinstance(_ia1,float) and np.isnan(_ia1)):
            _metrics.append(("ICC(A,1) — primary", f"{_ia1:.5f}",
                             _icc_r.get("icc_2_1_label","—")))

        _ccc2 = (_grp_res.get("lin_ccc") or {}).get("ccc")
        if _ccc2 is not None and not (isinstance(_ccc2,float) and np.isnan(_ccc2)):
            _metrics.append(("Lin's CCC", f"{_ccc2:.5f}",
                             (_grp_res.get("lin_ccc") or {}).get("label","—")))

        _ka2 = (_grp_res.get("krippendorff") or {}).get("alpha")
        if _ka2 is not None and not (isinstance(_ka2,float) and np.isnan(_ka2)):
            _metrics.append(("Krippendorff's α", f"{_ka2:.5f}",
                             (_grp_res.get("krippendorff") or {}).get("label","—")))

        # Display in 3-column grid
        if _metrics:
            _ncols = min(3, len(_metrics))
            _cols = st.columns(_ncols)
            for _mi, (_lbl, _val, _interp) in enumerate(_metrics):
                with _cols[_mi % _ncols]:
                    st.markdown(
                        f'<div style="background:white;border:1px solid #e2e8f0;'
                        f'border-radius:6px;padding:10px;text-align:center;'
                        f'margin-bottom:8px;">'
                        f'<div style="font-size:1.1rem;font-weight:700;color:#1a1a2e;">'
                        f'{_val}</div>'
                        f'<div style="font-size:.73rem;color:#64748b;font-weight:600;">'
                        f'{_lbl}</div>'
                        f'<div style="font-size:.68rem;color:#94a3b8;margin-top:2px;">'
                        f'{_interp}</div>'
                        f'</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Benchmark reference note
    st.markdown(
        '<div style="background:#f0f9ff;border-left:3px solid #0284c7;'
        'padding:10px 14px;border-radius:4px;font-size:.77rem;color:#1e3a5f;'
        'margin-bottom:12px;">'
        '<b>Benchmark References:</b> '
        'Kappa family — Landis & Koch (1977): &lt;0 Poor; 0.00–0.20 Slight; '
        '0.21–0.40 Fair; 0.41–0.60 Moderate; 0.61–0.80 Substantial; '
        '0.81–1.00 Almost Perfect. '
        'ICC / CCC — Koo & Li (2016): &lt;0.50 Poor; 0.50–0.75 Moderate; '
        '0.75–0.90 Good; &gt;0.90 Excellent. '
        'Krippendorff (2004): α&ge;0.800 reliable; 0.667&le;α&lt;0.800 tentatively acceptable. '
        '"—" = method not applicable for this data type / rater count. '
        'See each group\'s tab below for full detail, visualisations, and interpretation.'
        '</div>',
        unsafe_allow_html=True)
else:
    # ── Internal Consistency summary ──────────────────────────────────────
    st.markdown('<div class="sec-title">Reliability Summary (All Constructs)</div>',
                unsafe_allow_html=True)
    srows = [list(M["summary"].columns)] + [
        [_f(v) if isinstance(v,(int,float,np.floating)) else str(v)
         for v in M["summary"].loc[i]] for i in M["summary"].index]
    st.markdown(html_tbl(srows, left_cols={0}), unsafe_allow_html=True)
    if figs_b and figs_b[0] is not None:
        st.image(figs_b[0], use_container_width=True)
    st.markdown('<p class="note-txt">Figures only \u2014 a quick numeric comparison. '
                'Full detail per coefficient in each tab below.</p>',
                unsafe_allow_html=True)

ctabs = st.tabs([res["construct_name"] for res in M["constructs"]] + ["\U0001f4dd Notes"])
for ti, res in enumerate(M["constructs"]):
    with ctabs[ti]:
        if rel_mode == "Inter-Rater Agreement":
            # ── Error guard: display informative message if group failed ──
            if res.get("error"):
                st.error(
                    f"&#9888;&#65039; **{res.get('construct_name', f'Group {ti+1}')}** "
                    f"could not be analysed: {res['error']}")
                continue

            # ── NEW: clean per-group display from run_multi_irar ─────────
            from modules.reliability import _get_applicable_methods
            name         = res.get("construct_name", f"Group {ti+1}")
            irar_dtype   = res.get("data_type","")
            r_names      = res.get("rater_names",[])
            applicable   = res.get("applicable_methods",[])
            n_units      = res.get("n_units",0)
            k_raters     = res.get("k_raters",0)
            method_ctx   = res.get("method_context",{})

            # Context banner — academic English, professional
            st.markdown(
                f'<div class="decision-banner use-param">&#128202; '
                f'<b>{irar_dtype.title()} data</b> &nbsp;|&nbsp; '
                f'<b>{k_raters} raters</b> &nbsp;|&nbsp; '
                f'<b>{n_units} units</b> &nbsp;|&nbsp; '
                f'<b>{len(applicable)} methods computed</b></div>',
                unsafe_allow_html=True)

            # Method context description
            if method_ctx:
                with st.expander("📋 Method Selection Rationale & Guidance"):
                    st.markdown(
                        f'<div class="norm-rec-box">'
                        f'{method_ctx.get("methods","")}<br/><br/>'
                        f'<b>Guidance for this configuration:</b><br/>'
                        f'{method_ctx.get("guidance","")}'
                        f'</div>', unsafe_allow_html=True)

            # Method tabs
            method_tab_names = {
                "pct":          "% Agreement",
                "cohen":        "Cohen's κ",
                "gwet_ac1":     "Gwet's AC1",
                "scott_pi":     "Scott's π",
                "bp":           "Brennan-Prediger",
                "fleiss":       "Fleiss' κ",
                "weighted":     "Weighted κ",
                "gwet_ac2":     "Gwet's AC2",
                "icc":          "ICC",
                "ccc":          "Lin's CCC",
                "krippendorff": "Krippendorff's α",
            }
            tab_labels = [method_tab_names.get(m, m) for m in applicable]
            if not tab_labels:
                st.warning("No applicable methods for this configuration.")
            else:
                mtabs = st.tabs(tab_labels)
                for mi, mkey in enumerate(applicable):
                    with mtabs[mi]:

                        # ── Percentage Agreement ──────────────────────────
                        if mkey == "pct":
                            pa_res = res.get("percentage_agreement") or {}
                            if not pa_res:
                                st.info("Percentage Agreement not computed.")
                            else:
                                _pa = pa_res.get("pa", np.nan)
                                _lo = pa_res.get("ci_lo", np.nan)
                                _hi = pa_res.get("ci_hi", np.nan)
                                try: _ci_pa=_fmt_ci(_lo, _hi)
                                except: _ci_pa="—"
                                c1,c2,c3=st.columns(3)
                                c1.metric("Percentage Agreement",
                                          f"{_pa*100:.1f}%" if not np.isnan(_pa) else "—")
                                c2.metric("95% CI", _ci_pa)
                                c3.metric("N units / Raters",
                                          f"{n_units} / {k_raters}")
                                _total_pairs = pa_res.get("total_pairwise_comparisons",
                                                            n_units*k_raters*(k_raters-1)//2)
                                rows=[["Statistic","Value"],
                                      ["Percentage Agreement",
                                       f"{_pa*100:.2f}%" if not np.isnan(_pa) else "—"],
                                      ["As proportion", _f(_pa)],
                                      ["95% CI (binomial)", _ci_pa],
                                      ["N (units)", str(n_units)],
                                      ["k (raters)", str(k_raters)],
                                      ["Total pairwise comparisons", str(_total_pairs)]]
                                st.markdown(html_tbl(rows,left_cols={0}),
                                            unsafe_allow_html=True)

                                # ── Per-unit descriptive statistics ───────
                                # Matches the variable a researcher would
                                # construct for descriptive-statistics analysis: one
                                # agreement proportion per rated unit, then
                                # Mean/SD/Min/Max across units.
                                _pu_mean = pa_res.get("mean", np.nan)
                                _pu_sd   = pa_res.get("sd", np.nan)
                                _pu_min  = pa_res.get("minimum", np.nan)
                                _pu_max  = pa_res.get("maximum", np.nan)
                                _n_valid = pa_res.get("n_units_valid", 0)
                                if _n_valid > 0:
                                    st.markdown(
                                        '<div class="sub-title">Per-Unit Agreement — '
                                        'Descriptive Statistics</div>',
                                        unsafe_allow_html=True)
                                    desc_rows = [["Statistic", "Value"],
                                        ["N (units with \u22651 valid pair)", str(_n_valid)],
                                        ["Minimum", _f(_pu_min)],
                                        ["Maximum", _f(_pu_max)],
                                        ["Mean", _f(_pu_mean)],
                                        ["Std. Deviation", _f(_pu_sd)]]
                                    st.markdown(html_tbl(desc_rows, left_cols={0}),
                                                unsafe_allow_html=True)
                                    _pu_gap = (abs(_pu_mean - _pa)
                                               if (not np.isnan(_pu_mean) and not np.isnan(_pa))
                                               else np.nan)
                                    st.markdown(
                                        '<p class="note-txt">The Mean above is the average '
                                        'of PER-UNIT agreement proportions (one value per '
                                        'rated unit \u2014 the proportion of that unit\u2019s '
                                        'rater-pairs that agreed exactly), matching what a '
                                        'DESCRIPTIVES-style analysis on a per-unit agreement '
                                        'variable would report. It differs conceptually from '
                                        'the POOLED Percentage Agreement above (which pools '
                                        'all rater-pairs across all units into one '
                                        'proportion) but is numerically equal to it when '
                                        'every unit has the same number of valid rater-pairs '
                                        f'(here, gap = {_f(_pu_gap)}). '
                                        'A non-zero Std. Deviation indicates agreement is not '
                                        'uniform across units \u2014 the Minimum/Maximum show '
                                        'the range of unit-level agreement observed, which the '
                                        'single pooled proportion alone cannot reveal. '
                                        'Purpose: identifies whether disagreement is spread '
                                        'evenly across units or concentrated in a subset of '
                                        'problematic units. Reference: Stemler, S.E. (2004). '
                                        'Practical Assessment, Research &amp; Evaluation, 9(4).'
                                        '</p>', unsafe_allow_html=True)
                                # Visual: PA gauge (same standard as Krippendorff)
                                try:
                                    _pagauge = _irar_pa_gauge(
                                        _pa, _lo, _hi,
                                        f"Percentage Agreement — {name}")
                                    if _pagauge:
                                        st.image(fig_to_bytes(_pagauge),
                                                 use_container_width=True)
                                        plt.close("all")
                                except Exception:
                                    pass
                                st.markdown(
                                    '<p class="note-txt">Percentage Agreement does not correct '
                                    'for chance agreement. It is reported as a descriptive '
                                    'baseline only. Always report alongside a chance-corrected '
                                    'coefficient (Cohen\'s κ, Gwet\'s AC1, or Krippendorff\'s α). '
                                    'Reference: Stemler (2004). Practical Assessment, Research '
                                    '&amp; Evaluation, 9(4).</p>',
                                    unsafe_allow_html=True)
                                it=pa_res.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',
                                                   unsafe_allow_html=True)

                        # ── Cohen's κ ────────────────────────────────────
                        elif mkey == "cohen":
                            ck = res.get("cohen_kappa") or {}
                            if not ck:
                                st.info("Cohen's κ not computed for this group.")
                            else:
                                variants = ck.get("variants", {})
                                _kv=ck.get("kappa",np.nan); _klbl=ck.get("kappa_label","—")
                                _kp=ck.get("kappa_p",np.nan)
                                c1,c2,c3=st.columns(3)
                                c1.metric("Cohen's κ (unweighted)",_f(_kv))
                                c2.metric("Interpretation",_klbl.split(" (")[0] if _klbl else "—")
                                c3.metric("Sig.(2-tailed)",_p(_kp) if not np.isnan(_kp) else "—")

                                st.markdown(
                                    f'<p class="note-txt">Rater 1: {ck.get("rater1","—")} | '
                                    f'Rater 2: {ck.get("rater2","—")} | N: {ck.get("n",n_units)} | '
                                    f'Categories: {ck.get("n_categories","—")}</p>',
                                    unsafe_allow_html=True)

                                # ── Confusion matrix / Agreement Table ──
                                ct=ck.get("crosstab")
                                if ct is not None:
                                    st.markdown('<div class="sub-title">Agreement Table</div>',
                                                unsafe_allow_html=True)
                                    ct_rows=[[""] + [str(c) for c in ct.columns]]
                                    for idx in ct.index:
                                        ct_rows.append([str(idx)]+[str(ct.loc[idx,c]) for c in ct.columns])
                                    st.markdown(html_tbl(ct_rows,left_cols={0}),unsafe_allow_html=True)
                                    r1n=r_names[0] if r_names else "Rater 1"
                                    r2n=r_names[1] if len(r_names)>1 else "Rater 2"
                                    hm=_irar_kappa_heatmap(ct, r1n, r2n,
                                                           f"Confusion Matrix — {name}")
                                    if hm:
                                        st.image(fig_to_bytes(hm),use_container_width=True)
                                        plt.close("all")

                                # ── Kappa Results: SEMUA 3 skema sekaligus ──
                                st.markdown('<div class="sub-title">Kappa Results (All Weighting Schemes)</div>',
                                            unsafe_allow_html=True)
                                scheme_rows = [["Scheme","κ","SE (null, Eq.9)","SE (general, Eq.8)","z","Sig.(2-tailed)","Interpretation"]]
                                for scheme_key, scheme_label in [("unweighted","Unweighted"),
                                                                   ("linear","Linear"),
                                                                   ("quadratic","Quadratic")]:
                                    v = variants.get(scheme_key, {})
                                    scheme_rows.append([
                                        scheme_label,
                                        _f(v.get("kappa",np.nan)),
                                        _f(v.get("se_null",np.nan)),
                                        _f(v.get("se_general",np.nan)),
                                        _f(v.get("z",np.nan)),
                                        _p(v.get("p",np.nan)) if not np.isnan(v.get("p",np.nan)) else "—",
                                        v.get("label","—").split(" (")[0] if v.get("label") else "—",
                                    ])
                                st.markdown(html_tbl(scheme_rows,left_cols={0}),unsafe_allow_html=True)
                                st.markdown(
                                    '<p class="note-txt">For k=2 categories, all three schemes are '
                                    'mathematically identical (only one inter-category distance is '
                                    'possible) — per Fleiss, J.L., &amp; Cohen, J. (1973). Educational '
                                    'and Psychological Measurement, 33(3), 613–619. They diverge for '
                                    '3+ ordered categories.</p>', unsafe_allow_html=True)

                                # ── Agreement Breakdown ──
                                st.markdown('<div class="sub-title">Agreement Breakdown</div>',
                                            unsafe_allow_html=True)
                                st.markdown(f'<p class="note-txt">{ck.get("agreement_breakdown_text","")}</p>',
                                            unsafe_allow_html=True)

                                # ── Per-Category Agreement ──
                                per_cat = ck.get("per_category", [])
                                if per_cat:
                                    st.markdown('<div class="sub-title">Per-Category Agreement</div>',
                                                unsafe_allow_html=True)
                                    pc_rows = [["Category","N (Rater 1)","N (Rater 2)","Agree","Pct"]]
                                    for row in per_cat:
                                        pc_rows.append([
                                            str(row["category"]), str(row["n_r1"]), str(row["n_r2"]),
                                            str(row["agree"]),
                                            f'{row["pct"]:.1f}%' if not np.isnan(row["pct"]) else "—"])
                                    st.markdown(html_tbl(pc_rows,left_cols={0}),unsafe_allow_html=True)
                                    st.markdown(
                                        '<p class="note-txt">Pct = Agree / (N_Rater1 + N_Rater2 − Agree), '
                                        'a Jaccard-style (intersection-over-union) same-category '
                                        'concordance rate.</p>', unsafe_allow_html=True)

                                if ck.get("dtype") == "dichotomous":
                                    st.markdown(
                                        f'<p class="note-txt"><b>Prevalence Index:</b> '
                                        f'{_f(ck.get("prevalence_index",np.nan))} &nbsp;|&nbsp; '
                                        f'<b>Bias Index:</b> {_f(ck.get("bias_index",np.nan))}</p>',
                                        unsafe_allow_html=True)

                                _ck_ci_note = ck.get("kappa_ci_note","")
                                if _ck_ci_note:
                                    st.markdown(f'<p class="note-txt"><b>Why no confidence interval:</b> {_ck_ci_note}</p>',unsafe_allow_html=True)

                                # ── Referensi lengkap ──
                                _ref_note = ck.get("formula_reference_note","")
                                if _ref_note:
                                    st.markdown(
                                        f'<div class="sub-title">References</div>'
                                        f'<p class="note-txt">{_ref_note}</p>',
                                        unsafe_allow_html=True)

                                it=ck.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',
                                                   unsafe_allow_html=True)

                        # Weighted Cohen's κ
                        elif mkey == "weighted":
                            wk = res.get("weighted_kappa") or {}
                            if not wk:
                                st.info("Weighted Cohen's κ not computed.")
                            else:
                                _kwq=wk.get("kappa_quadratic",np.nan)
                                _kwl=wk.get("kappa_linear",np.nan)
                                _ku=wk.get("kappa",np.nan)
                                _lbl=wk.get("kappa_quadratic_label","—")
                                c1,c2,c3=st.columns(3)
                                c1.metric("κ_w (quadratic — primary)",_f(_kwq))
                                c2.metric("κ_w (linear)",_f(_kwl))
                                c3.metric("κ (unweighted)",_f(_ku))
                                rows=[["Statistic","Value","SE","z","Sig."],
                                      ["κ (unweighted)",_f(_ku),_f(wk.get("kappa_ase")),
                                       _f(wk.get("kappa_z")),_p(wk.get("kappa_p"))],
                                      ["κ_w (linear)",_f(_kwl),_f(wk.get("kappa_linear_ase")),
                                       _f(wk.get("kappa_linear_z")),_p(wk.get("kappa_linear_p"))],
                                      ["κ_w (quadratic — primary)",_f(_kwq),_f(wk.get("kappa_quadratic_ase")),
                                       _f(wk.get("kappa_quadratic_z")),_p(wk.get("kappa_quadratic_p"))]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                # Visual: multi-value bar — quadratic primary on top
                                try:
                                    _wk_vals = {
                                        "κ_w (quadratic) ★": float(_kwq) if not np.isnan(float(_kwq)) else np.nan,
                                        "κ_w (linear)":       float(_kwl) if not np.isnan(float(_kwl)) else np.nan,
                                        "κ (unweighted)":     float(_ku)  if not np.isnan(float(_ku))  else np.nan,
                                    }
                                    _wk_colors = ["#e94560","#0284c7","#94a3b8"]
                                    _wfig, _wax = plt.subplots(figsize=(8.5, 2.5))
                                    _wlbls = list(_wk_vals.keys())
                                    _wdisp = [max(min(v,1.05),-0.22) if not np.isnan(v) else 0.0
                                              for v in _wk_vals.values()]
                                    _wax.barh(_wlbls, _wdisp, color=_wk_colors,
                                              edgecolor="white", height=0.45, zorder=3)
                                    for thr, col in [(0.40,"#f59e0b"),(0.60,"#0284c7"),(0.80,"#16a34a")]:
                                        _wax.axvline(thr, color=col, ls="--", lw=0.9, alpha=0.45, zorder=1)
                                    _wax.axvline(0, color="#334155", lw=0.9, zorder=2)
                                    _wax.set_xlim(min(-0.22, min(_wdisp)-0.05), 1.18)
                                    _wax.set_xlabel("Kappa value", fontsize=9, color=PAL[0])
                                    _wax.set_title(f"Weighted Cohen's κ — {name}  (★ primary)",
                                                   fontsize=10, fontweight="bold", color=PAL[0])
                                    for _bi, (_lk, _bv) in enumerate(zip(_wlbls, _wdisp)):
                                        _rv = list(_wk_vals.values())[_bi]
                                        if not np.isnan(_rv):
                                            _bx = _bv+0.04 if _bv>=0 else _bv-0.04
                                            _wax.text(_bx, _bi, f"{_rv:.3f}", va="center",
                                                      ha="left" if _bv>=0 else "right",
                                                      fontsize=9, fontweight="bold", color=PAL[0],
                                                      zorder=5, bbox=dict(boxstyle="round,pad=0.15",
                                                      fc="white", ec="none", alpha=0.90))
                                    _wax.spines[["top","right"]].set_visible(False)
                                    _wfig.patch.set_facecolor("white")
                                    _wfig.tight_layout(pad=1.3)
                                    st.image(fig_to_bytes(_wfig), use_container_width=True)
                                    plt.close("all")
                                except Exception:
                                    pass
                                st.markdown(f'<p class="note-txt"><b>Primary</b>: κ_w (quadratic) = {_f(_kwq)} — {_lbl}.<br/>'
                                            f'{wk.get("formula_note","")}</p>',unsafe_allow_html=True)
                                ct=wk.get("crosstab")
                                if ct is not None:
                                    st.markdown('<div class="sub-title">Confusion Matrix</div>',unsafe_allow_html=True)
                                    ct_rows=[[""] + [str(c) for c in ct.columns]]
                                    for idx in ct.index:
                                        ct_rows.append([str(idx)]+[str(ct.loc[idx,c]) for c in ct.columns])
                                    st.markdown(html_tbl(ct_rows,left_cols={0}),unsafe_allow_html=True)
                                    hm=_irar_kappa_heatmap(ct,
                                        r_names[0] if r_names else "Rater 1",
                                        r_names[1] if len(r_names)>1 else "Rater 2",
                                        f"Confusion Matrix — {name}")
                                    if hm: st.image(fig_to_bytes(hm),use_container_width=True); plt.close("all")
                                it=wk.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # Fleiss' κ
                        elif mkey == "fleiss":
                            fk = res.get("fleiss_kappa") or {}
                            if not fk:
                                st.info("Fleiss' κ not computed.")
                            else:
                                _fk=fk.get("kappa",np.nan); _flbl=fk.get("kappa_label","—")
                                _fp2=fk.get("kappa_p",np.nan)
                                c1,c2,c3=st.columns(3)
                                c1.metric("Fleiss' κ",_f(_fk))
                                c2.metric("Interpretation",_flbl.split(" (")[0] if _flbl else "—")
                                c3.metric("Sig.(2-tailed)",_p(_fp2) if not np.isnan(_fp2) else "—")
                                rows=[["Statistic","Value"],
                                      ["Fleiss' κ",_f(_fk)],
                                      ["P\u0304 (observed agreement)",_f(fk.get("P_bar",np.nan))],
                                      ["P\u0304_e (expected/chance agreement)",_f(fk.get("P_e",np.nan))],
                                      ["SE",_f(fk.get("kappa_se",np.nan))],
                                      ["z",_f(fk.get("kappa_z",np.nan))],
                                      ["Sig.(2-tailed)",_p(_fp2) if not np.isnan(_fp2) else "—"],
                                      ["95% CI","Not reported \u2014 see note below"],
                                      ["Interpretation",_flbl],
                                      ["N (units)",str(n_units)],["k (raters)",str(k_raters)]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                pc=fk.get("kappa_per_category",{})
                                if pc:
                                    st.markdown('<div class="sub-title">Per-Category κ</div>',unsafe_allow_html=True)
                                    pc_rows=[["Category","κ_j","p̂ (proportion)"]]
                                    for cat,kv in pc.items():
                                        pv=fk.get("p_per_category",{}).get(cat,np.nan)
                                        pc_rows.append([str(cat),_f(kv),_f(pv)])
                                    st.markdown(html_tbl(pc_rows,left_cols={0}),unsafe_allow_html=True)
                                st.markdown(f'<p class="note-txt">{fk.get("formula_note","")}</p>',unsafe_allow_html=True)
                                _fk_ci_note = fk.get("kappa_ci_note","")
                                if _fk_ci_note:
                                    st.markdown(f'<p class="note-txt"><b>Why no confidence interval:</b> {_fk_ci_note}</p>',unsafe_allow_html=True)
                                it=fk.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # ICC
                        elif mkey == "icc":
                            icc = res.get("icc") or {}
                            if "error" in icc:
                                st.error(f"⚠️ ICC: {icc['error']}")
                            elif not icc:
                                st.info("ICC not computed.")
                            else:
                                def _fv(v):
                                    try: return _f(v) if not (isinstance(v,float) and np.isnan(v)) else "—"
                                    except: return "—"
                                _p21=icc.get("icc_2_1",np.nan)
                                # Fix [8]: metric card labels kept short to prevent truncation
                                # Full label in the detail table below
                                _plbl_short = (icc.get("icc_2_1_label","—") or "—").split(" ")[0]
                                _p2k=icc.get("icc_2_k",np.nan)
                                c1,c2,c3=st.columns(3)
                                c1.metric("ICC(A,1) — Primary",_fv(_p21))
                                c2.metric("ICC(A,k)",_fv(_p2k))
                                c3.metric("Interpretation",_plbl_short)
                                rows=[["ICC Form","Description","ICC","95% CI","p (F-test)"],
                                      ["ICC(1,1)",
                                       "One-way random, single rater",
                                       _fv(icc.get("icc_1_1","—")),
                                       _fmt_ci(icc.get("icc_1_1_ci_lo",np.nan),icc.get("icc_1_1_ci_hi",np.nan)),
                                       _fmt_p_dash(icc.get("icc_1_1_p",np.nan))],
                                      ["ICC(A,1) — PRIMARY",
                                       "Two-way random, absolute agreement, single rater",
                                       _fv(icc.get("icc_2_1")),
                                       _fmt_ci(icc.get("icc_2_1_ci_lo",np.nan),icc.get("icc_2_1_ci_hi",np.nan)),
                                       _fmt_p_dash(icc.get("icc_2_1_p",np.nan))],
                                      ["ICC(C,1)",
                                       "Two-way mixed, consistency, single rater",
                                       _fv(icc.get("icc_3_1")),
                                       _fmt_ci(icc.get("icc_3_1_ci_lo",np.nan),icc.get("icc_3_1_ci_hi",np.nan)),
                                       _fmt_p_dash(icc.get("icc_3_1_p",np.nan))],
                                      ["ICC(1,k)",
                                       f"One-way random, mean of {k_raters} raters",
                                       _fv(icc.get("icc_1_k","—")),
                                       _fmt_ci(icc.get("icc_1_k_ci_lo",np.nan),icc.get("icc_1_k_ci_hi",np.nan)),
                                       _fmt_p_dash(icc.get("icc_1_k_p",np.nan))],
                                      ["ICC(A,k)",
                                       f"Two-way random, absolute agreement, mean of {k_raters} raters",
                                       _fv(icc.get("icc_2_k")),
                                       _fmt_ci(icc.get("icc_2_k_ci_lo",np.nan),icc.get("icc_2_k_ci_hi",np.nan)),
                                       _fmt_p_dash(icc.get("icc_2_k_p",np.nan))],
                                      ["ICC(C,k)",
                                       f"Two-way mixed, consistency, mean of {k_raters} raters",
                                       _fv(icc.get("icc_3_k")),
                                       _fmt_ci(icc.get("icc_3_k_ci_lo",np.nan),icc.get("icc_3_k_ci_hi",np.nan)),
                                       _fmt_p_dash(icc.get("icc_3_k_p",np.nan))]]
                                st.markdown(html_tbl(rows,left_cols={0,1}),unsafe_allow_html=True)
                                _icc_fig = _irar_icc_bar(icc, f"ICC — {name}")
                                if _icc_fig:
                                    st.image(fig_to_bytes(_icc_fig), use_container_width=True)
                                    plt.close("all")
                                st.markdown(f'<p class="note-txt">{icc.get("formula_note","")}</p>',unsafe_allow_html=True)
                                st.markdown(
                                    '<p class="note-txt"><b>Model in this context:</b> ICC here treats '
                                    'the actual raters in this group as independent assessors of the '
                                    'same rated units \u2014 this is agreement between distinct raters. '
                                    '<b>This differs from the Internal Consistency module\u2019s ICC</b>, '
                                    'where items (not raters) are treated as interchangeable measures of '
                                    'a construct within respondents. <b>When to use this (Inter-Rater) '
                                    'context vs the Internal Consistency context:</b> use this context '
                                    'when your question is about agreement between raters; use the '
                                    'Internal Consistency module when your question is about a scale\u2019s '
                                    'item-level consistency. Both share identical underlying mathematics '
                                    '(Shrout &amp; Fleiss, 1979) but answer different substantive '
                                    'questions. <b>ICC(A,1)</b> is the primary estimate here because '
                                    'absolute agreement (penalising systematic rater bias) is typically '
                                    'the more relevant standard for inter-rater work.</p>',
                                    unsafe_allow_html=True)
                                it=icc.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # Krippendorff's α
                        elif mkey == "krippendorff":
                            ka = res.get("krippendorff") or {}
                            if not ka:
                                st.info("Krippendorff's α not computed.")
                            else:
                                _kav=ka.get("alpha",np.nan); _klbl=ka.get("label","—")
                                _nb=ka.get("n_boot",1000)
                                _lo=ka.get("ci_lo",np.nan); _hi=ka.get("ci_hi",np.nan)
                                try: _kci=_fmt_ci(_lo, _hi)
                                except: _kci="—"
                                c1,c2,c3=st.columns(3)
                                c1.metric("Krippendorff's α",_f(_kav))
                                c2.metric(f"95% CI ({_nb:,} resamples)",_kci)
                                c3.metric("Interpretation",_klbl.split(" (")[0] if _klbl else "—")
                                rows=[["Statistic","Value"],
                                      ["Krippendorff's α",_f(_kav)],
                                      [f"95% CI ({_nb:,} bootstrap resamples)",_kci],
                                      ["Data type / metric",ka.get("data_type","—").title()],
                                      ["N (units)",str(n_units)],
                                      ["k (raters)",str(k_raters)],
                                      ["Threshold — min acceptable","α ≥ 0.667 (Krippendorff, 2004)"],
                                      ["Threshold — reliable","α ≥ 0.800 (Krippendorff, 2004)"],
                                      ["Interpretation",_klbl]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                _kg = _irar_kripp_gauge(_kav, _klbl, f"Krippendorff's α — {name}")
                                if _kg:
                                    st.image(fig_to_bytes(_kg), use_container_width=True)
                                    plt.close("all")
                                st.markdown(f'<p class="note-txt">{ka.get("formula_note","")}</p>',unsafe_allow_html=True)
                                it=ka.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # ── Gwet's AC1 ────────────────────────────────────
                        elif mkey == "gwet_ac1":
                            ac1 = res.get("gwet_ac1") or {}
                            if not ac1 or ac1.get("ac1") is None:
                                st.info("Gwet's AC1 not computed.")
                            else:
                                _av=ac1.get("ac1",np.nan); _albl=ac1.get("label","—")
                                _ase=ac1.get("se",np.nan); _az=ac1.get("z",np.nan)
                                _ap=ac1.get("p",np.nan)
                                _alo_z=ac1.get("ci_lo_z",np.nan); _ahi_z=ac1.get("ci_hi_z",np.nan)
                                _alo_t=ac1.get("ci_lo_t",np.nan); _ahi_t=ac1.get("ci_hi_t",np.nan)
                                try: _aci_z=_fmt_ci(_alo_z, _ahi_z)
                                except: _aci_z="—"
                                try: _aci_t=_fmt_ci(_alo_t, _ahi_t)
                                except: _aci_t="—"
                                c1,c2,c3=st.columns(3)
                                c1.metric("Gwet's AC1",_f(_av))
                                c2.metric("95% CI (z-basis)",_aci_z)
                                c3.metric("Interpretation",_albl.split(" (")[0] if _albl else "—")
                                rows=[["Statistic","Value"],
                                      ["Gwet's AC1",_f(_av)],
                                      ["SE (jackknife)",_f(_ase)],
                                      ["z",_f(_az)],
                                      ["p (2-tailed)",_p(_ap) if not np.isnan(_ap) else "—"],
                                      ["95% CI (z-basis)",_aci_z],
                                      ["95% CI (t-basis, df="+str(ac1.get("ci_df","—"))+")",_aci_t],
                                      ["N (units)",str(n_units)],
                                      ["k (raters)",str(k_raters)],
                                      ["q (categories)",str(ac1.get("q","—"))],
                                      ["Interpretation",_albl]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                # Visual: single bar
                                try:
                                    _ac1fig = _irar_single_bar(_av, _albl, "Gwet's AC1", name)
                                    if _ac1fig:
                                        st.image(fig_to_bytes(_ac1fig), use_container_width=True)
                                        plt.close("all")
                                except Exception: pass
                                st.markdown(f'<p class="note-txt">{ac1.get("formula_note","")}</p>',unsafe_allow_html=True)
                                if ac1.get("dual_ci_note"):
                                    st.markdown(ac1["dual_ci_note"], unsafe_allow_html=True)
                                it=ac1.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # ── Scott's π ─────────────────────────────────────
                        elif mkey == "scott_pi":
                            sp = res.get("scott_pi") or {}
                            if not sp or np.isnan(sp.get("pi",np.nan)):
                                st.info("Scott's π not computed.")
                            else:
                                _sv2=sp.get("pi",np.nan); _slbl=sp.get("label","—")
                                _sse=sp.get("se",np.nan); _sz=sp.get("z",np.nan); _spp=sp.get("p",np.nan)
                                _slo_z=sp.get("ci_lo_z",np.nan); _shi_z=sp.get("ci_hi_z",np.nan)
                                _slo_t=sp.get("ci_lo_t",np.nan); _shi_t=sp.get("ci_hi_t",np.nan)
                                try: _sci_z=_fmt_ci(_slo_z, _shi_z)
                                except: _sci_z="—"
                                try: _sci_t=_fmt_ci(_slo_t, _shi_t)
                                except: _sci_t="—"
                                c1,c2,c3=st.columns(3)
                                c1.metric("Scott's π",_f(_sv2))
                                c2.metric("95% CI (z-basis)",_sci_z)
                                c3.metric("Interpretation",_slbl.split(" (")[0] if _slbl else "—")
                                rows=[["Statistic","Value"],
                                      ["Scott's π",_f(_sv2)],
                                      ["P_o (observed)",_f(sp.get("Po",np.nan))],
                                      ["P_e (Scott averaged marginals)",_f(sp.get("Pe",np.nan))],
                                      ["SE",_f(_sse)],["z",_f(_sz)],
                                      ["p (2-tailed)",_p(_spp) if not np.isnan(_spp) else "—"],
                                      ["95% CI (z-basis)",_sci_z],
                                      ["95% CI (t-basis, df="+str(sp.get("ci_df","—"))+")",_sci_t],
                                      ["N (units)",str(n_units)],
                                      ["Interpretation",_slbl]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                # Visual
                                try:
                                    _spfig = _irar_single_bar(_sv2, _slbl, "Scott's π", name)
                                    if _spfig:
                                        st.image(fig_to_bytes(_spfig), use_container_width=True)
                                        plt.close("all")
                                except Exception: pass
                                if sp.get("dual_ci_note"):
                                    st.markdown(sp["dual_ci_note"], unsafe_allow_html=True)
                                it=sp.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # ── Brennan-Prediger ───────────────────────────────
                        elif mkey == "bp":
                            bp_r = res.get("brennan_prediger") or {}
                            if not bp_r or np.isnan(bp_r.get("kappa_bp",np.nan)):
                                st.info("Brennan-Prediger coefficient not computed.")
                            else:
                                _bv=bp_r.get("kappa_bp",np.nan); _blbl=bp_r.get("label","—")
                                _bse=bp_r.get("se",np.nan); _bz=bp_r.get("z",np.nan)
                                _bpp=bp_r.get("p",np.nan)
                                _blo_z=bp_r.get("ci_lo_z",np.nan); _bhi_z=bp_r.get("ci_hi_z",np.nan)
                                _blo_t=bp_r.get("ci_lo_t",np.nan); _bhi_t=bp_r.get("ci_hi_t",np.nan)
                                try: _bci_z=_fmt_ci(_blo_z, _bhi_z)
                                except: _bci_z="—"
                                try: _bci_t=_fmt_ci(_blo_t, _bhi_t)
                                except: _bci_t="—"
                                c1,c2,c3=st.columns(3)
                                c1.metric("Brennan-Prediger",_f(_bv))
                                c2.metric("95% CI (z-basis)",_bci_z)
                                c3.metric("Interpretation",_blbl.split(" (")[0] if _blbl else "—")
                                rows=[["Statistic","Value"],
                                      ["Brennan-Prediger (κ_BP)",_f(_bv)],
                                      ["P_o (observed agreement)",_f(bp_r.get("Po",np.nan))],
                                      ["P_e (= 1/q — uniform)",_f(bp_r.get("Pe",np.nan))],
                                      ["q (categories)",str(bp_r.get("q","—"))],
                                      ["SE",_f(_bse)],["z",_f(_bz)],
                                      ["p (2-tailed)",_p(_bpp) if not np.isnan(_bpp) else "—"],
                                      ["95% CI (z-basis)",_bci_z],
                                      ["95% CI (t-basis, df="+str(bp_r.get("ci_df","—"))+")",_bci_t],
                                      ["N (units)",str(n_units)],
                                      ["Interpretation",_blbl]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                try:
                                    _bpfig = _irar_single_bar(_bv, _blbl, "Brennan-Prediger", name)
                                    if _bpfig:
                                        st.image(fig_to_bytes(_bpfig), use_container_width=True)
                                        plt.close("all")
                                except Exception: pass
                                if bp_r.get("dual_ci_note"):
                                    st.markdown(bp_r["dual_ci_note"], unsafe_allow_html=True)
                                _bp_cmp = bp_r.get("comparison_table")
                                if _bp_cmp:
                                    st.markdown(
                                        '<div class="sub-title">Comparison with Other Coefficients</div>',
                                        unsafe_allow_html=True)
                                    _cmp_rows = [["Coefficient", "Value", "Chance-Agreement Model"]]
                                    for _cname, _cval, _cdesc in _bp_cmp:
                                        _cmp_rows.append([_cname, _f(_cval), _cdesc])
                                    st.markdown(html_tbl(_cmp_rows, left_cols={0,2}),
                                                unsafe_allow_html=True)
                                    if bp_r.get("comparison_note"):
                                        st.markdown(f'<p class="note-txt">{bp_r["comparison_note"]}</p>',
                                                    unsafe_allow_html=True)
                                it=bp_r.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)

                        # ── Gwet's AC2 — all five weighting schemes ────────
                        elif mkey == "gwet_ac2":
                            ac2_all = res.get("gwet_ac2") or {}
                            _schemes = ac2_all.get("schemes", {})
                            _computed = {k: v for k, v in _schemes.items()
                                         if v.get("ac2") is not None and not np.isnan(v.get("ac2", np.nan))}
                            if not _computed:
                                st.info("Gwet's AC2 not computed.")
                            else:
                                st.markdown(
                                    '<p class="note-txt">Gwet\u2019s AC2 is computed under '
                                    '<b>all five standard weighting schemes</b> below, so the '
                                    'sensitivity of the result to the choice of weighting '
                                    'function is directly visible; no single scheme is '
                                    'selected on the user\u2019s behalf.</p>',
                                    unsafe_allow_html=True)
                                _scheme_order = ["quadratic", "linear", "radical", "ordinal", "identity"]
                                for _sk in _scheme_order:
                                    if _sk not in _computed:
                                        continue
                                    ac2 = _computed[_sk]
                                    _a2v=ac2.get("ac2",np.nan); _a2lbl=ac2.get("label","—")
                                    _a2se=ac2.get("se",np.nan); _a2z=ac2.get("z",np.nan)
                                    _a2p=ac2.get("p",np.nan)
                                    _a2lo_z=ac2.get("ci_lo_z",np.nan); _a2hi_z=ac2.get("ci_hi_z",np.nan)
                                    _a2lo_t=ac2.get("ci_lo_t",np.nan); _a2hi_t=ac2.get("ci_hi_t",np.nan)
                                    try: _a2ci_z=_fmt_ci(_a2lo_z, _a2hi_z)
                                    except: _a2ci_z="—"
                                    try: _a2ci_t=_fmt_ci(_a2lo_t, _a2hi_t)
                                    except: _a2ci_t="—"
                                    st.markdown(
                                        f'<div class="sub-title">{ac2.get("scheme_label", _sk.title())}</div>',
                                        unsafe_allow_html=True)
                                    c1,c2,c3=st.columns(3)
                                    c1.metric(f"Gwet's AC2 ({_sk})",_f(_a2v))
                                    c2.metric("95% CI (z-basis)",_a2ci_z)
                                    c3.metric("Interpretation",_a2lbl.split(" (")[0] if _a2lbl else "—")
                                    rows=[["Statistic","Value"],
                                          [f"Gwet's AC2 ({ac2.get('scheme_label','')})",_f(_a2v)],
                                          ["SE (jackknife)",_f(_a2se)],
                                          ["z",_f(_a2z)],
                                          ["p (2-tailed)",_p(_a2p) if not np.isnan(_a2p) else "—"],
                                          ["95% CI (z-basis)",_a2ci_z],
                                          ["95% CI (t-basis, df="+str(ac2.get("ci_df","—"))+")",_a2ci_t],
                                          ["N (units)",str(n_units)],
                                          ["k (raters)",str(k_raters)],
                                          ["q (categories)",str(ac2.get("q","—"))],
                                          ["Weight function",ac2.get("weight_formula","—")],
                                          ["Interpretation",_a2lbl]]
                                    st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                    if ac2.get("when_to_use"):
                                        st.markdown(
                                            f'<p class="note-txt"><b>When to use this scheme:</b> '
                                            f'{ac2["when_to_use"]}</p>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="note-txt">{ac2.get("formula_note","")}</p>',unsafe_allow_html=True)
                                    if ac2.get("dual_ci_note"):
                                        st.markdown(ac2["dual_ci_note"], unsafe_allow_html=True)
                                    it=ac2.get("interpretation_text","")
                                    if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)
                                    st.markdown("---")


                        # ── Lin's CCC ─────────────────────────────────────
                        elif mkey == "ccc":
                            ccc_r = res.get("lin_ccc") or {}
                            if not ccc_r or ccc_r.get("ccc") is None:
                                st.info("Lin's CCC not computed.")
                            else:
                                _cv=ccc_r.get("ccc",np.nan); _clbl=ccc_r.get("label","—")
                                _crho=ccc_r.get("rho",np.nan); _cCb=ccc_r.get("Cb",np.nan)
                                _clo=ccc_r.get("ci_lo",np.nan); _chi2=ccc_r.get("ci_hi",np.nan)
                                try: _cci=_fmt_ci(_clo, _chi2)
                                except: _cci="—"
                                c1,c2,c3=st.columns(3)
                                c1.metric("Lin's CCC (ρ_c)",_f(_cv))
                                c2.metric("95% CI (Fisher z)",_cci)
                                c3.metric("Interpretation",_clbl.split(" (")[0] if _clbl else "—")
                                rows=[["Statistic","Value","Interpretation"],
                                      ["CCC (ρ_c) — overall concordance",_f(_cv),_clbl],
                                      ["Pearson r (ρ) — precision",_f(_crho),
                                       "How correlated the two raters are"],
                                      ["r² (r-squared)",_f(_crho**2) if not np.isnan(_crho) else "—",""],
                                      ["Bias correction factor (C_b) — accuracy",
                                       _f(_cCb) if not (isinstance(_cCb,float) and np.isnan(_cCb)) else "—",
                                       "1.0 = no bias; < 1 = systematic bias present"],
                                      ["Mean (Rater/Method 1)",_f(ccc_r.get("mean1",np.nan)),""],
                                      ["Mean (Rater/Method 2)",_f(ccc_r.get("mean2",np.nan)),""],
                                      ["Mean difference",_f(ccc_r.get("mean_diff",np.nan)),""],
                                      ["SD (Rater/Method 1)",_f(ccc_r.get("sd1",np.nan)),""],
                                      ["SD (Rater/Method 2)",_f(ccc_r.get("sd2",np.nan)),""],
                                      ["Location shift (u)",_f(ccc_r.get("u_shift",np.nan)),
                                       "Mean gap relative to pooled scale"],
                                      ["Scale shift (v)",_f(ccc_r.get("v_shift",np.nan)),
                                       "Ratio of the two SDs"],
                                      ["95% CI (Fisher z-transform)",_cci,""],
                                      ["N (units)",str(n_units),""],
                                      ["CCC ≤ Pearson r",
                                       "Always true" if not (np.isnan(_cv) or np.isnan(_crho)) and _cv<=_crho else "—",
                                       "Gap = extent of systematic bias"]]
                                st.markdown(html_tbl(rows,left_cols={0}),unsafe_allow_html=True)
                                # Visual: precision vs accuracy decomposition
                                try:
                                    _cfig,_cax=plt.subplots(figsize=(7,2.5))
                                    _vals=[max(min(float(v),1.0),-0.2) if not (isinstance(v,float) and np.isnan(v)) else 0
                                           for v in [_cv,_crho,_cCb]]
                                    _labels=["CCC ρ_c\n(overall)","Pearson r\n(precision)","C_b\n(accuracy)"]
                                    _cols=["#e94560","#0284c7","#16a34a"]
                                    _cax.barh(_labels,_vals,color=_cols,edgecolor="white",height=0.5)
                                    for thr,col in [(0.75,"#0284c7","Good"),(0.90,"#16a34a","Excellent")]:
                                        _cax.axvline(thr,color=col,ls="--",lw=0.9,alpha=0.7)
                                        _cax.text(thr,len(_labels)-0.1,f"≥{thr}",ha="center",
                                                  fontsize=7,color=col)
                                    _cax.axvline(0,color=PAL[0],lw=0.8)
                                    _cax.set_xlim(-0.1,1.10)
                                    _cax.set_xlabel("Value",fontsize=9,color=PAL[0])
                                    _cax.set_title(f"Lin's CCC — Precision vs Accuracy — {name}",
                                                  fontsize=10,fontweight="bold",color=PAL[0])
                                    for i,v in enumerate(_vals):
                                        _cax.text(v+0.02,i,f"{v:.3f}",va="center",fontsize=9,color=PAL[0])
                                    _cax.spines[["top","right"]].set_visible(False)
                                    _cfig.patch.set_facecolor("white"); _cfig.tight_layout()
                                    st.image(fig_to_bytes(_cfig),use_container_width=True); plt.close("all")
                                except Exception: pass
                                st.markdown(f'<p class="note-txt">{ccc_r.get("formula_note","")}</p>',unsafe_allow_html=True)
                                st.markdown(
                                    '<p class="note-txt"><b>95% CI methodology:</b> Fisher-Z transformation '
                                    'using the FULL large-sample variance formula from Lin (1989, Biometrics '
                                    '45:255\u2013268; see also Lin, Hedayat, Sinha &amp; Yang, 2002, JASA '
                                    '97(457):257\u2013270) \u2014 this accounts for both precision (r) AND the '
                                    'location-shift/bias term (u) shown above, not a simplified '
                                    'matched-means-only approximation.</p>', unsafe_allow_html=True)
                                it=ccc_r.get("interpretation_text","")
                                if it: st.markdown(f'<div class="interp-box sig">{it}</div>',unsafe_allow_html=True)
        else:
            # ── Internal Consistency rendering (unchanged) ────────────────
            a = res["alpha"]
            cls = "use-param" if (a == a and a >= 0.7) else "use-nonparam"
            st.markdown(
                f'<div class="decision-banner {cls}">Cronbach\u2019s \u03b1 = {_f(a)} '
                f'\u2014 <b>{alpha_label(a)}</b> internal consistency '
                f'({res["k"]} items, N = {res["n"]})</div>', unsafe_allow_html=True)
            if res.get("flagged_reverse") and not res.get("reverse_info"):
                st.warning("\u26a0\ufe0f Possible reverse-scored item(s): "
                           f"{', '.join(res['flagged_reverse'])}. "
                           "Enable auto-reverse in the sidebar if appropriate.")

            blocks = _coeff_blocks(res, alpha)
            stabs = st.tabs([b["title"] for b in blocks] + ["Item Statistics"])
            for si, blk in enumerate(blocks):
                with stabs[si]:
                    if blk.get("sections"):
                        # Multi-section tab: several logically-distinct results
                        # (e.g. omega_t + omega_h, or raw-basis + standardized-
                        # basis lambdas) grouped under one tab with their own
                        # sub-headings, rather than scattered across separate
                        # top-level tabs.
                        for sec in blk["sections"]:
                            st.markdown(f'<div class="sub-title">{sec["heading"]}</div>',
                                        unsafe_allow_html=True)
                            if sec.get("cards"):
                                cols = st.columns(len(sec["cards"]))
                                for c, (lab, val, sub) in zip(cols, sec["cards"]):
                                    c.markdown(
                                        f'<div class="metric-card"><div class="metric-val">{val}</div>'
                                        f'<div class="metric-lbl">{lab}</div>'
                                        f'<div style="font-size:.72rem;color:#e94560;font-weight:600;'
                                        f'margin-top:2px;">{sub}</div></div>', unsafe_allow_html=True)
                                st.markdown("")
                            if sec.get("table"):
                                st.markdown(html_tbl([sec["table"][0]] + sec["table"][1],
                                                    left_cols=sec.get("table_left", {0})),
                                            unsafe_allow_html=True)
                                if sec.get("table_note"):
                                    st.markdown(f'<p class="note-txt">{sec["table_note"]}</p>',
                                                unsafe_allow_html=True)
                            if sec.get("table2"):
                                st.markdown(html_tbl([sec["table2"][0]] + sec["table2"][1],
                                                    left_cols=sec.get("table_left", {0})),
                                            unsafe_allow_html=True)
                                if sec.get("table2_note"):
                                    st.markdown(f'<p class="note-txt">{sec["table2_note"]}</p>',
                                                unsafe_allow_html=True)
                            if sec.get("interp"):
                                st.markdown(f'<div class="interp-box sig">{sec["interp"]}</div>',
                                            unsafe_allow_html=True)
                            if sec.get("params"):
                                st.markdown(f'<p class="note-txt"><b>Decision parameters:</b> '
                                            f'{sec["params"]}</p>', unsafe_allow_html=True)
                            if sec.get("note"):
                                st.markdown(f'<p class="note-txt">{sec["note"]}</p>',
                                            unsafe_allow_html=True)
                            st.markdown("---")
                        continue
                    cols = st.columns(len(blk["cards"]))
                    for c, (lab, val, sub) in zip(cols, blk["cards"]):
                        c.markdown(
                            f'<div class="metric-card"><div class="metric-val">{val}</div>'
                            f'<div class="metric-lbl">{lab}</div>'
                            f'<div style="font-size:.72rem;color:#e94560;font-weight:600;'
                            f'margin-top:2px;">{sub}</div></div>', unsafe_allow_html=True)
                    st.markdown("")
                    if blk["table"]:
                        st.markdown(html_tbl([blk["table"][0]] + blk["table"][1],
                                            left_cols=blk.get("table_left", {0})),
                                    unsafe_allow_html=True)
                        if blk.get("table_note"):
                            st.markdown(f'<p class="note-txt">{blk["table_note"]}</p>',
                                        unsafe_allow_html=True)
                    if blk.get("table2"):
                        st.markdown(html_tbl([blk["table2"][0]] + blk["table2"][1],
                                            left_cols=blk.get("table_left", {0})),
                                    unsafe_allow_html=True)
                        if blk.get("table2_note"):
                            st.markdown(f'<p class="note-txt">{blk["table2_note"]}</p>',
                                        unsafe_allow_html=True)
                    if blk.get("footnote"):
                        st.markdown(f'<p class="note-txt">{blk["footnote"]}</p>',
                                    unsafe_allow_html=True)
                    st.markdown(f'<div class="interp-box sig">{blk["interp"]}</div>',
                                unsafe_allow_html=True)
                    st.markdown(f'<p class="note-txt"><b>Decision parameters:</b> '
                                f'{blk["params"]}</p>', unsafe_allow_html=True)
                    if blk["note"]:
                        st.markdown(f'<p class="note-txt">{blk["note"]}</p>',
                                    unsafe_allow_html=True)
                    # Item-level diagnostics (KR-20 out-of-range)
                    if blk.get("item_diag"):
                        st.markdown('<div class="sub-title">Item Diagnostics '
                                    '(p and p\u00d7q per item)</div>',
                                    unsafe_allow_html=True)
                        st.markdown(html_tbl(blk["item_diag"], left_cols={0, 3}),
                                    unsafe_allow_html=True)
                        st.markdown('<p class="note-txt">p = proportion of respondents '
                                    'answering 1 (correct/endorsed). '
                                    'p\u00d7q = item variance for dichotomous items. '
                                    'Items with p &lt; .10 or p &gt; .90 contribute '
                                    'near-zero variance and cause KR-20 to exceed 1.</p>',
                                    unsafe_allow_html=True)
            with stabs[-1]:
                for tname, payload in _item_tables(res).items():
                    st.markdown(f'<div class="sub-title">{tname}</div>',
                                unsafe_allow_html=True)
                    if tname == "Item-Total Statistics":
                        cols, rows, neg = payload
                        st.markdown(html_tbl([cols] + rows, left_cols={0}),
                                    unsafe_allow_html=True)
                        if neg:
                            st.markdown('<p class="note-txt">a. A negative value '
                                        'indicates a negative average covariance among '
                                        'items, violating reliability model assumptions '
                                        '\u2014 check item codings (possible reverse item).</p>',
                                        unsafe_allow_html=True)
                        f = figs_b[ti + 1]
                        if f is not None:
                            st.image(f, use_container_width=True)
                    else:
                        cols, rows = payload
                        st.markdown(html_tbl([cols] + rows, left_cols={0}),
                                    unsafe_allow_html=True)
                scols, srows2 = _scale_rows(res)
                st.markdown('<div class="sub-title">Scale Statistics</div>',
                            unsafe_allow_html=True)
                st.markdown(html_tbl([scols] + srows2, left_cols={0}),
                            unsafe_allow_html=True)
                if res.get("reverse_info"):
                    ritems = "; ".join(f"{it}: {f}" for it, f in res["reverse_info"])
                    st.markdown(f'<p class="note-txt">Reverse-scored items applied: '
                                f'{ritems}.</p>', unsafe_allow_html=True)

with ctabs[-1]:
    st.markdown('<div class="sec-title">Methodological Notes</div>',
                unsafe_allow_html=True)
    for title, txt in _methodological_notes(M, alpha):
        st.markdown(f'<div class="norm-rec-box"><b>{title}.</b> {txt}</div>',
                    unsafe_allow_html=True)

# ── Downloads ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### &#128229; Export")
dc1, dc2 = st.columns(2)
with dc1:
    with st.spinner("Generating HTML report\u2026"):
        html_data = _build_html(M, meta, figs_b, alpha)
    st.download_button("&#127760; HTML Report (Full)", html_data,
                       f"Reliability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                       "text/html", use_container_width=True)
with dc2:
    csv_data = _build_csv(M, meta, alpha)
    st.download_button("&#128221; CSV Tables", csv_data,
                       f"Reliability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       "text/csv", use_container_width=True)
