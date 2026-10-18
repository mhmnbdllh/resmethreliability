"""
utils/tables.py
===============
HTML table builders for statistical output in Streamlit UI.
All functions return HTML strings rendered via st.markdown(unsafe_allow_html=True).
"""

import pandas as pd
import numpy as np
from utils.formatters import _f, _p


# ══════════════════════════════════════════════════════════════════════════════
# CORE TABLE BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def html_tbl(rows, left_cols=None, center_cols=None, highlight_cols=None):
    """
    Build a formatted HTML table from a list of rows.

    Parameters
    ----------
    rows : list of list
        First row is the header. Subsequent rows are data.
    left_cols : set of int, optional
        Column indices to left-align. Default: {0}.
    center_cols : set of int, optional
        Column indices to center-align (overrides default right-align).
    highlight_cols : set of int, optional
        Column indices to apply highlight styling.

    Returns
    -------
    str : HTML string ready for st.markdown(unsafe_allow_html=True)
    """
    if left_cols is None:
        left_cols = {0}
    if center_cols is None:
        center_cols = set()
    if highlight_cols is None:
        highlight_cols = set()

    html = '<div class="stat-tbl-wrap"><table class="stat-tbl"><thead><tr>'
    for cell in rows[0]:
        html += f"<th>{cell}</th>"
    html += "</tr></thead><tbody>"

    for row in rows[1:]:
        html += "<tr>"
        for i, v in enumerate(row):
            if i in left_cols:
                css = ' class="left"'
            elif i in center_cols:
                css = ' style="text-align:center;"'
            elif i in highlight_cols:
                css = ' style="color:#e94560;font-weight:700;"'
            else:
                css = ""
            html += f"<td{css}>{v}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def df_to_rows(df):
    """
    Convert a pandas DataFrame to a list of rows suitable for html_tbl().
    First row is column headers; subsequent rows are string-formatted data.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    list of list of str
    """
    rows = [list(df.columns)]
    for _, r in df.iterrows():
        rows.append([str(v) for v in r.values])
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# SPECIALISED TABLE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def descriptives_table(desc_df):
    """
    Format and render a descriptive statistics DataFrame as an HTML table.

    Parameters
    ----------
    desc_df : pd.DataFrame
        Output of run_*() R['desc'].

    Returns
    -------
    str : HTML table string
    """
    dd = desc_df.copy()
    for c in dd.select_dtypes(include=[float, np.float64]).columns:
        dd[c] = dd[c].apply(_f)
    return html_tbl(df_to_rows(dd))


def normality_table(norm_list, primary_label):
    """
    Build SW and KS normality tables with pass/fail indicators.

    Parameters
    ----------
    norm_list : list of dict
        Output of modules/normality.py test_normality().
    primary_label : str
        'Shapiro-Wilk' or 'Kolmogorov-Smirnov'

    Returns
    -------
    tuple of (sw_html, ks_html) : str, str
    """
    sw_rows = [["Variable", "N", "Statistic (W)", "Sig.", "Result"]]
    ks_rows = [["Variable", "N", "Statistic (D)", "Sig.\u1d43", "Result"]]

    for nm in norm_list:
        sw_res = ('<span class="pass">&#10003; Normal</span>'
                  if nm["sw_pass"]
                  else '<span class="fail">&#10007; Non-Normal</span>')
        ks_res = ('<span class="pass">&#10003; Normal</span>'
                  if nm["ks_pass"]
                  else '<span class="fail">&#10007; Non-Normal</span>')
        sw_rows.append([
            nm["label"], str(nm["n"]),
            _f(nm["sw_W"]), _p(nm["sw_p"]), sw_res
        ])
        ks_rows.append([
            nm["label"], str(nm["n"]),
            _f(nm["ks_D"]), _p(nm["ks_p"]), ks_res
        ])

    return (
        html_tbl(sw_rows, left_cols={0, 4}),
        html_tbl(ks_rows, left_cols={0, 4})
    )


def assumption_summary_table(R, use_p, prim_lbl, total_n):
    """
    Build the Assumption Summary table.
    SW and KS are displayed as separate rows per variable for readability.

    Parameters
    ----------
    R        : dict  — full results dict from run_*()
    use_p    : bool  — True if parametric analysis applied
    prim_lbl : str   — primary normality criterion label
    total_n  : int   — total N of the analysis

    Returns
    -------
    str : HTML table string
    """
    rows = [["Assumption", "Test", "Statistic", "Sig.", "Result", "Decision"]]

    for nm in R["normality"]:
        passed    = nm["pass"]
        is_sw_pri = nm["primary_label"] == "Shapiro-Wilk"
        is_ks_pri = nm["primary_label"] == "Kolmogorov-Smirnov"

        # SW row
        rows.append([
            f"Normality \u2014 {nm['label']}",
            f"Shapiro-Wilk{'&#9733;' if is_sw_pri else ''}",
            f"W\u2009=\u2009{_f(nm['sw_W'])}",
            _p(nm["sw_p"]),
            ('<span class="pass">&#10003; Normal</span>'
             if nm["sw_pass"]
             else '<span class="fail">&#10007; Non-Normal</span>'),
            "Primary criterion" if is_sw_pri else "Supplementary"
        ])
        # KS row
        rows.append([
            "",
            f"KS Lilliefors{'&#9733;' if is_ks_pri else ''}",
            f"D\u2009=\u2009{_f(nm['ks_D'])}",
            _p(nm["ks_p"]),
            ('<span class="pass">&#10003; Normal</span>'
             if nm["ks_pass"]
             else '<span class="fail">&#10007; Non-Normal</span>'),
            "Primary criterion" if is_ks_pri else "Supplementary"
        ])

    # Levene (if present)
    if "levene" in R:
        lev = R["levene"]
        rows.append([
            "Homogeneity of Variance",
            "Levene\u2019s Test",
            f"F({lev['df1']},\u2009{lev['df2']})\u2009=\u2009{_f(lev['F'])}",
            _p(lev["Sig."]),
            ('<span class="pass">&#10003; Satisfied</span>'
             if lev["equal_var"]
             else '<span class="fail">&#10007; Violated</span>'),
            "Equal variances assumed" if lev["equal_var"]
            else "Welch correction applied"
        ])

    # Overall decision
    rows.append([
        "<b>Overall Decision</b>",
        f"Primary: {prim_lbl}",
        f"Total N\u2009=\u2009{total_n}",
        "\u2014",
        f'<b>{"&#10003; Parametric" if use_p else "&#9888; Non-parametric"}</b>',
        f'<b>{"T-Test applied" if use_p else "Wilcoxon / Mann-Whitney U"}</b>'
    ])

    return html_tbl(rows, left_cols={0, 1, 2, 5})


def levene_table(lev):
    """
    Build a Levene's Test result table.

    Parameters
    ----------
    lev : dict — R['levene']

    Returns
    -------
    str : HTML table string
    """
    res = ('<span class="pass">&#10003; Equal variances assumed</span>'
           if lev["equal_var"]
           else '<span class="fail">&#10007; Equal variances not assumed (Welch)</span>')

    return html_tbl([
        ["F", "df1", "df2", "Sig.", "Result"],
        [_f(lev["F"]), str(lev["df1"]), str(lev["df2"]),
         _p(lev["Sig."]), res]
    ], left_cols={4})


def correlation_table(corr_df):
    """
    Build a Paired Samples Correlations table.

    Parameters
    ----------
    corr_df : pd.DataFrame — R['correlation']

    Returns
    -------
    str : HTML table string
    """
    co = corr_df.copy()
    co["Pearson Correlation"] = co["Pearson Correlation"].apply(_f)
    co["Sig. (2-tailed)"]     = co["Sig. (2-tailed)"].apply(_p)
    return html_tbl(df_to_rows(co), left_cols={0})


def effect_size_table(np_r, test_type, pr):
    """
    Build a Non-Parametric Effect Size table (Rank-Biserial r + Bootstrap CI).
    Interpretation guide is placed as a note below the table, not inside it.

    Parameters
    ----------
    np_r      : dict  — R['nonparametric']
    test_type : str
    pr        : dict  — R['parametric']

    Returns
    -------
    tuple of (table_html, note_html) : str, str
    """
    from utils.formatters import _f as fmt

    r_rb  = np_r.get("rank_biserial_r", np.nan)
    ci_lo = np_r.get("rb_ci_lower", np.nan)
    ci_hi = np_r.get("rb_ci_upper", np.nan)
    r_lab = np_r.get("rb_label", "N/A")

    if test_type == "Independent-Sample T-Test":
        es_label  = "Mann-Whitney U"
        pair_desc = f"{np_r['label1']} vs. {np_r['label2']}"
    elif test_type == "Paired-Sample T-Test":
        es_label  = "Wilcoxon Signed-Rank"
        pair_desc = f"{pr['label1']} \u2212 {pr['label2']}"
    else:
        es_label  = "Wilcoxon Signed-Rank"
        pair_desc = f"Variable \u2212 \u03bc\u2080"

    ci_str = (f"[{fmt(ci_lo)}, {fmt(ci_hi)}]"
              if not (np.isnan(ci_lo) or np.isnan(ci_hi)) else ".")

    tbl = html_tbl([
        ["Test", "Comparison", "Rank-Biserial r", "95% Bootstrap CI", "Effect Size"],
        [es_label, pair_desc,
         fmt(r_rb) if not np.isnan(r_rb) else ".",
         ci_str, r_lab]
    ], left_cols={0, 1})

    note = (
        '<p class="note-txt">'
        'Rank-biserial r \u2208 [\u22121,\u20091]: '
        '|r|\u2009&lt;\u2009.10 negligible, '
        '.10\u2013.29 small, .30\u2013.49 medium, \u2265\u2009.50 large. '
        'Non-parametric effect size not reported by SPSS by default. '
        'Bootstrap 95% CI based on 2,000 resamples '
        '(Efron &amp; Tibshirani, 1993; Kerby, 2014).'
        '</p>'
    )
    return tbl, note


def power_table(pw, alpha):
    """
    Build a Statistical Power Assessment table with colour-coded progress bar.

    Parameters
    ----------
    pw    : dict — output of modules/power.py compute_power()
    alpha : float

    Returns
    -------
    tuple of (table_html, bar_html, note_html) : str, str, str
    """
    pwr_val = pw.get("power", np.nan)
    pwr_pct = f"{pwr_val * 100:.1f}%" if not np.isnan(pwr_val) else "N/A"
    pwr_lbl = pw.get("power_label", "N/A")
    eff_v   = pw.get("effect_size", np.nan)
    eff_t   = pw.get("effect_type", "\u2014")
    n_desc  = (f"n\u2081\u2009=\u2009{pw['n1']}, n\u2082\u2009=\u2009{pw['n2']}"
               if "n1" in pw else f"n\u2009=\u2009{pw.get('n', 'N/A')}")

    rows = [
        ["Parameter", "Value"],
        ["Sample size",              n_desc],
        ["Observed effect size",     f"{_f(eff_v)} ({eff_t})"],
        ["Significance level (\u03b1)", str(alpha)],
        ["Achieved statistical power", pwr_pct],
        ["Power classification",     pwr_lbl],
        ["Recommended minimum",      "\u2265\u2009.80 (Cohen, 1988)"],
    ]
    tbl = html_tbl(rows, left_cols={0})

    # Colour-coded progress bar
    if not np.isnan(pwr_val):
        bar_colour = ("#16a34a" if pwr_val >= .80
                      else "#f59e0b" if pwr_val >= .60
                      else "#dc2626")
        bar_pct = int(pwr_val * 100)
        bar = (
            f'<div style="background:#e2e8f0;border-radius:8px;'
            f'height:18px;width:100%;margin:8px 0;">'
            f'<div style="background:{bar_colour};width:{bar_pct}%;'
            f'height:18px;border-radius:8px;"></div></div>'
        )
    else:
        bar = ""

    note = (
        '<p class="note-txt">'
        'Post-hoc power analysis uses the observed effect size and sample size '
        'to estimate the probability of correctly rejecting H\u2080 given that '
        'the effect is real. Computed via the non-central t-distribution '
        '(parametric) or normal approximation (non-parametric). '
        'Reference: Cohen (1988).'
        '</p>'
    )
    return tbl, bar, note


# ══════════════════════════════════════════════════════════════════════════════
# ONE-SAMPLE T-TEST TABLE
# ══════════════════════════════════════════════════════════════════════════════

def one_sample_parametric_table(pr):
    """
    Build the One-Sample T-Test result table.

    Parameters
    ----------
    pr : dict — R['parametric']

    Returns
    -------
    str : HTML table string
    """
    from utils.formatters import effect_label_d
    return html_tbl([
        ["", "t", "df", "Sig. (2-tailed)",
         "Sig. (1-tailed Lower)", "Sig. (1-tailed Upper)",
         "Mean Difference", "95% CI Lower", "95% CI Upper",
         "Cohen\u2019s d", "Effect Size"],
        [f"Test Value\u2009=\u2009{pr['mu0']}",
         _f(pr["t"]), str(pr["df"]),
         _p(pr["p_two"]),
         _p(pr["p_one_lower"]), _p(pr["p_one_upper"]),
         _f(pr["mean_diff"]),
         _f(pr["ci_lower"]), _f(pr["ci_upper"]),
         _f(pr["cohens_d"]), effect_label_d(pr["cohens_d"])]
    ], left_cols={0, 10})


# ══════════════════════════════════════════════════════════════════════════════
# PAIRED-SAMPLE T-TEST TABLES
# ══════════════════════════════════════════════════════════════════════════════

def paired_parametric_table(pr):
    """
    Build the Paired Samples T-Test result table.

    Parameters
    ----------
    pr : dict — R['parametric']

    Returns
    -------
    str : HTML table string
    """
    from utils.formatters import effect_label_d
    return html_tbl([
        ["Pair", "Mean Difference", "Std. Deviation", "Std. Error Mean",
         "95% CI Lower", "95% CI Upper", "t", "df",
         "Sig. (2-tailed)", "Sig. (1-tailed L)", "Sig. (1-tailed U)",
         "Cohen\u2019s d"],
        [f"{pr['label1']} \u2013 {pr['label2']}",
         _f(pr["mean_diff"]), _f(pr["sd_diff"]), _f(pr["se_diff"]),
         _f(pr["ci_lower"]), _f(pr["ci_upper"]),
         _f(pr["t"]), str(pr["df"]),
         _p(pr["p_two"]),
         _p(pr["p_one_lower"]), _p(pr["p_one_upper"]),
         _f(pr["cohens_d"])]
    ], left_cols={0})


# ══════════════════════════════════════════════════════════════════════════════
# INDEPENDENT-SAMPLE T-TEST TABLES
# ══════════════════════════════════════════════════════════════════════════════

def independent_parametric_tables(pr, lev):
    """
    Build Independent Samples T-Test result tables (a and b).

    Parameters
    ----------
    pr  : dict — R['parametric']
    lev : dict — R['levene']

    Returns
    -------
    tuple of (table_a_html, table_b_html, note_html) : str, str, str
    """
    from utils.formatters import effect_label_d

    tbl_a = html_tbl([
        ["", "F (Levene)", "Sig.", "t", "df",
         "Sig. (2-tailed)", "Sig. (1-tailed L)", "Sig. (1-tailed U)"],
        ["Equal variances assumed",
         _f(lev["F"]), _p(lev["Sig."]),
         _f(pr["t_eq"]), str(pr["df_eq"]), _p(pr["p_eq"]),
         _p(pr["p_eq_lower"]), _p(pr["p_eq_upper"])],
        ["Equal variances not assumed", "", "",
         _f(pr["t_welch"]), _f(pr["df_welch"], 2), _p(pr["p_welch"]),
         _p(pr["p_welch_lower"]), _p(pr["p_welch_upper"])]
    ], left_cols={0})

    tbl_b = html_tbl([
        ["", "Mean Difference", "SE Difference",
         "95% CI Lower", "95% CI Upper", "Cohen\u2019s d"],
        ["Equal variances assumed",
         _f(pr["mean_diff"]), _f(pr["se_eq"]),
         _f(pr["ci_eq_l"]), _f(pr["ci_eq_u"]), _f(pr["cohens_d"])],
        ["Equal variances not assumed",
         _f(pr["mean_diff"]), _f(pr["se_welch"]),
         _f(pr["ci_welch_l"]), _f(pr["ci_welch_u"]), "\u2014"]
    ], left_cols={0})

    active = ("Row 1 (equal variances assumed)"
              if lev["equal_var"] else "Row 2 (Welch correction)")
    note = (
        f'<p class="note-txt">Based on Levene\u2019s test '
        f'p\u2009=\u2009{_p(lev["Sig."])}: use <b>{active}</b>.</p>'
    )
    return tbl_a, tbl_b, note


# ══════════════════════════════════════════════════════════════════════════════
# NON-PARAMETRIC TABLES (WILCOXON & MANN-WHITNEY)
# ══════════════════════════════════════════════════════════════════════════════

def wilcoxon_tables(np_r, test_type, pr):
    """
    Build Wilcoxon Signed-Rank Test tables (Ranks + Test Statistics).

    Parameters
    ----------
    np_r      : dict — R['nonparametric']
    test_type : str
    pr        : dict — R['parametric']

    Returns
    -------
    tuple of (ranks_html, stats_html, footnotes_html) : str, str, str
    """
    from utils.formatters import format_u as fu

    n_neg  = np_r.get("n_neg", 0)
    n_pos  = np_r.get("n_pos", 0)
    n_ties = np_r.get("n_ties", 0)
    n_tot  = np_r.get("n_total", n_neg + n_pos + n_ties)
    neg_rs = np_r.get("neg_rank_sum", np.nan)
    pos_rs = np_r.get("pos_rank_sum", np.nan)
    neg_mr = neg_rs / n_neg if n_neg > 0 else np.nan
    pos_mr = pos_rs / n_pos if n_pos > 0 else np.nan

    fn_exist = (test_type == "Paired-Sample T-Test")
    footnotes = []
    if fn_exist:
        footnotes = [
            f"\u1d43 {pr['label2']} &lt; {pr['label1']} (negative difference)",
            f"\u1d47 {pr['label2']} &gt; {pr['label1']} (positive difference)",
            f"\u1d9c {pr['label2']} = {pr['label1']} "
            f"(zero difference; excluded from ranking)"
        ]

    ranks_html = html_tbl([
        ["", "N", "Mean Rank", "Sum of Ranks"],
        [("Negative Ranks \u1d43" if fn_exist else "Negative Ranks"),
         str(n_neg), _f(neg_mr), _f(neg_rs, 3)],
        [("Positive Ranks \u1d47" if fn_exist else "Positive Ranks"),
         str(n_pos), _f(pos_mr), _f(pos_rs, 3)],
        [("Ties \u1d9c" if fn_exist else "Ties"), str(n_ties), "", ""],
        ["Total", str(n_tot), "", ""]
    ], left_cols={0})

    pair_lbl = (f"{pr['label1']} \u2212 {pr['label2']}"
                if fn_exist else "Variable \u2212 \u03bc\u2080")
    stats_html = html_tbl([
        ["Statistic", pair_lbl],
        ["Test Statistic (W)", _f(np_r["W"], 3)],
        ["Z",                  _f(np_r["Z"])],
        ["Asymp. Sig. (2-tailed)", _p(np_r["p"])],
    ], left_cols={0})

    fn_html = "".join(
        f'<p class="note-txt">{fn}</p>' for fn in footnotes
    )
    fn_html += (
        f'<p class="note-txt">Based on '
        f'{"negative" if n_neg < n_pos else "positive"} ranks. '
        f'Z uses ties-corrected variance (SPSS method).</p>'
    )
    return ranks_html, stats_html, fn_html


def mannwhitney_tables(np_r):
    """
    Build Mann-Whitney U Test tables (Ranks + Test Statistics).

    Parameters
    ----------
    np_r : dict — R['nonparametric']

    Returns
    -------
    tuple of (ranks_html, stats_html, note_html) : str, str, str
    """
    from utils.formatters import format_u as fu

    ranks_html = html_tbl([
        ["Group", "N", "Mean Rank", "Sum of Ranks"],
        [np_r["label1"], str(np_r["n1"]),
         _f(np_r["mean_rank1"]), _f(np_r["R1"], 3)],
        [np_r["label2"], str(np_r["n2"]),
         _f(np_r["mean_rank2"]), _f(np_r["R2"], 3)],
        ["Total", str(np_r["n1"] + np_r["n2"]), "", ""]
    ], left_cols={0})

    stats_rows = [
        ["Statistic", "Value"],
        ["Mann-Whitney U",          fu(np_r["U"])],
        ["Wilcoxon W",              _f(np_r["W_wilcoxon"], 3)],
        ["Z",                       _f(np_r["Z"])],
        ["Asymp. Sig. (2-tailed)",  _p(np_r["p"])],
    ]
    p_ex = np_r.get("p_exact", float("nan"))
    import numpy as _np
    if not _np.isnan(p_ex):
        stats_rows.append(["Exact Sig. (2-tailed)", _p(p_ex)])
    stats_html = html_tbl(stats_rows, left_cols={0})

    note_html = (
        f'<p class="note-txt">'
        f'Grouping: {np_r["label1"]} vs.\u2009{np_r["label2"]}. '
        f'Z based on normal approximation with ties correction (SPSS method).'
        f'</p>'
    )
    return ranks_html, stats_html, note_html
