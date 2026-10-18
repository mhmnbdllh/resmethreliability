"""
utils/plots.py
==============
Diagnostic plots for all statistical tests.
All functions return matplotlib Figure objects.
Use fig_to_bytes() to convert to PNG bytes for Streamlit st.image()
or for embedding in HTML reports as base64.

Colour palette:
    PAL[0] = #1a1a2e  (dark navy   — primary)
    PAL[1] = #e94560  (crimson red — accent)
    PAL[2] = #0f3460  (deep blue   — secondary)
    PAL[3] = #16213e  (navy        — tertiary)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from io import BytesIO
from scipy import stats as scipy_stats

# ── Colour palette ─────────────────────────────────────────────────────────
PAL = ["#1a1a2e", "#e94560", "#0f3460", "#16213e"]
BG  = "#f8fafc"


# ══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def fig_to_bytes(fig, dpi=150):
    """
    Convert a matplotlib Figure to PNG bytes.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    dpi : int

    Returns
    -------
    bytes
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def _style_ax(ax):
    """Apply consistent axis styling."""
    ax.set_facecolor(BG)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#cbd5e1")
    ax.tick_params(colors="#64748b", labelsize=7)
    ax.xaxis.label.set_color("#64748b")
    ax.yaxis.label.set_color("#64748b")
    ax.title.set_color(PAL[0])


def _draw_qq(ax, data, color=None, label=None):
    """Draw a Normal Q-Q plot on the given axes."""
    if color is None:
        color = PAL[1]
    (osm, osr), (sl, ic, _) = scipy_stats.probplot(data)
    kw = {"label": label} if label else {}
    ax.plot(osm, osr, "o", color=color, markersize=5,
            markeredgecolor="white", markeredgewidth=.5,
            alpha=.85, **kw)
    ax.plot(osm, sl * np.array(osm) + ic,
            "--", color=PAL[0], lw=1.5, alpha=.7)
    ax.set_xlabel("Theoretical Quantiles", fontsize=8)
    ax.set_ylabel("Sample Quantiles", fontsize=8)


def _new_fig(ncols=3, figsize=None):
    """Create a new figure with GridSpec."""
    if figsize is None:
        figsize = (13, 4)
    fig = plt.figure(figsize=figsize, facecolor=BG)
    gs  = gridspec.GridSpec(1, ncols, figure=fig, wspace=.35)
    return fig, gs


# ══════════════════════════════════════════════════════════════════════════════
# ONE-SAMPLE T-TEST / WILCOXON SIGNED-RANK
# ══════════════════════════════════════════════════════════════════════════════

def plot_one_sample(data, mu0, var_name):
    """
    Diagnostic plots for One-Sample T-Test.
    Panel 1: Histogram with fitted normal curve + μ₀ and mean lines
    Panel 2: Normal Q-Q plot
    Panel 3: Box plot with μ₀ reference line

    Parameters
    ----------
    data     : array-like — observed values
    mu0      : float      — hypothesised population mean
    var_name : str        — variable name for axis labels

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = np.array(data, dtype=float)
    fig, gs = _new_fig(3)

    # ── Panel 1: Histogram ──────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    ax1.hist(data, bins="auto", color=PAL[1], alpha=0.72, edgecolor="white",
             linewidth=.8)
    xr = np.linspace(data.min() - 1, data.max() + 1, 300)
    sc = len(data) * (data.max() - data.min()) / max(len(data) // 3, 1)
    ax1.plot(xr,
             scipy_stats.norm.pdf(xr, data.mean(), data.std(ddof=1)) * sc,
             color=PAL[0], lw=2, alpha=.85)
    ax1.axvline(mu0, color=PAL[1], ls="--", lw=1.8,
                label=f"\u03bc\u2080\u2009=\u2009{mu0}")
    ax1.axvline(data.mean(), color=PAL[2], lw=1.8,
                label=f"x\u0304\u2009=\u2009{data.mean():.2f}")
    ax1.set_xlabel(var_name, fontsize=8)
    ax1.set_ylabel("Frequency", fontsize=8)
    ax1.set_title("Distribution", fontsize=9, fontweight="bold")
    ax1.legend(fontsize=7, framealpha=.7)

    # ── Panel 2: Q-Q plot ───────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    _draw_qq(ax2, data)
    ax2.set_title("Normal Q-Q Plot", fontsize=9, fontweight="bold")

    # ── Panel 3: Box plot ───────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    bp = ax3.boxplot(data, patch_artist=True, widths=0.5,
                     medianprops={"color": "white", "linewidth": 2.5},
                     boxprops={"facecolor": PAL[1], "alpha": 0.78},
                     whiskerprops={"color": PAL[0], "linewidth": 1.2},
                     capprops={"color": PAL[0], "linewidth": 1.2},
                     flierprops={"marker": "o", "color": PAL[1],
                                 "markersize": 4, "alpha": .7})
    ax3.axhline(mu0, color=PAL[1], ls="--", lw=1.8,
                label=f"\u03bc\u2080\u2009=\u2009{mu0}")
    ax3.set_xticklabels([var_name], fontsize=8)
    ax3.set_ylabel("Value", fontsize=8)
    ax3.set_title("Box Plot", fontsize=9, fontweight="bold")
    ax3.legend(fontsize=7, framealpha=.7)

    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAIRED-SAMPLE T-TEST / WILCOXON SIGNED-RANK
# ══════════════════════════════════════════════════════════════════════════════

def plot_paired(data1, data2, label1, label2):
    """
    Diagnostic plots for Paired-Sample T-Test.
    Panel 1: Individual change plot (spaghetti + mean line)
    Panel 2: Histogram of differences
    Panel 3: Side-by-side box plots

    Parameters
    ----------
    data1  : array-like — Variable 1 (pre / Time 1)
    data2  : array-like — Variable 2 (post / Time 2)
    label1 : str
    label2 : str

    Returns
    -------
    matplotlib.figure.Figure
    """
    data1 = np.array(data1, dtype=float)
    data2 = np.array(data2, dtype=float)
    diff  = data1 - data2
    fig, gs = _new_fig(3)

    # ── Panel 1: Individual changes ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    for v1, v2 in zip(data1, data2):
        ax1.plot([0, 1], [v1, v2], "-o",
                 color=PAL[2] if v2 >= v1 else PAL[1],
                 alpha=0.35, markersize=3.5, lw=.9)
    ax1.plot([0, 1], [data1.mean(), data2.mean()], "-o",
             color=PAL[1], lw=2.8, markersize=8,
             label="Group mean", zorder=5)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels([label1, label2], fontsize=9)
    ax1.set_ylabel("Value", fontsize=8)
    ax1.set_title("Individual Changes", fontsize=9, fontweight="bold")
    ax1.legend(fontsize=7, framealpha=.7)

    # ── Panel 2: Distribution of differences ────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    ax2.hist(diff, bins="auto", color=PAL[1], alpha=0.72, edgecolor="white",
             linewidth=.8)
    ax2.axvline(0, color=PAL[0], ls="--", lw=1.8, alpha=.8,
                label="Zero line")
    ax2.axvline(diff.mean(), color=PAL[2], lw=1.8,
                label=f"Mean\u2009=\u2009{diff.mean():.2f}")
    ax2.set_xlabel("Difference", fontsize=8)
    ax2.set_ylabel("Frequency", fontsize=8)
    ax2.set_title("Distribution of Differences", fontsize=9, fontweight="bold")
    ax2.legend(fontsize=7, framealpha=.7)

    # ── Panel 3: Box plots ───────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    ax3.boxplot([data1, data2], patch_artist=True, widths=0.5,
                medianprops={"color": "white", "linewidth": 2.5},
                boxprops={"facecolor": PAL[1], "alpha": 0.78},
                whiskerprops={"color": PAL[0], "linewidth": 1.2},
                capprops={"color": PAL[0], "linewidth": 1.2},
                flierprops={"marker": "o", "color": PAL[1],
                            "markersize": 4, "alpha": .7})
    ax3.set_xticklabels([label1, label2], fontsize=8)
    ax3.set_ylabel("Value", fontsize=8)
    ax3.set_title("Box Plots", fontsize=9, fontweight="bold")

    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# INDEPENDENT-SAMPLE T-TEST / MANN-WHITNEY U
# ══════════════════════════════════════════════════════════════════════════════

def plot_independent(g1, g2, label1, label2, dep_var):
    """
    Diagnostic plots for Independent-Sample T-Test.
    Panel 1: Side-by-side box plots by group
    Panel 2: Overlapping histograms by group
    Panel 3: Normal Q-Q plots by group

    Parameters
    ----------
    g1, g2   : array-like — group data
    label1   : str
    label2   : str
    dep_var  : str — dependent variable name

    Returns
    -------
    matplotlib.figure.Figure
    """
    g1 = np.array(g1, dtype=float)
    g2 = np.array(g2, dtype=float)
    fig, gs = _new_fig(3)

    # ── Panel 1: Box plots by group ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    bp  = ax1.boxplot([g1, g2], patch_artist=True, widths=0.5,
                      medianprops={"color": "white", "linewidth": 2.5},
                      whiskerprops={"color": PAL[0], "linewidth": 1.2},
                      capprops={"color": PAL[0], "linewidth": 1.2},
                      flierprops={"marker": "o", "markersize": 4, "alpha": .7})
    colors = [PAL[0], PAL[1]]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.78)
    for flier, c in zip(bp["fliers"], colors):
        flier.set_color(c)
    ax1.set_xticklabels([label1, label2], fontsize=8)
    ax1.set_ylabel(dep_var, fontsize=8)
    ax1.set_title("Box Plots by Group", fontsize=9, fontweight="bold")

    # ── Panel 2: Overlapping histograms ─────────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    all_min = min(g1.min(), g2.min())
    all_max = max(g1.max(), g2.max())
    bins = np.linspace(all_min - .5, all_max + .5, 16)
    ax2.hist(g1, bins=bins, color=PAL[0], alpha=0.62,
             label=label1, edgecolor="white", linewidth=.8)
    ax2.hist(g2, bins=bins, color=PAL[1], alpha=0.62,
             label=label2, edgecolor="white", linewidth=.8)
    ax2.set_xlabel(dep_var, fontsize=8)
    ax2.set_ylabel("Frequency", fontsize=8)
    ax2.set_title("Distribution by Group", fontsize=9, fontweight="bold")
    ax2.legend(fontsize=7, framealpha=.7)

    # ── Panel 3: Q-Q plots by group ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    for gd, c, lb in [(g1, PAL[0], label1), (g2, PAL[1], label2)]:
        (osm, osr), (sl, ic, _) = scipy_stats.probplot(gd)
        ax3.plot(osm, osr, "o", color=c, markersize=4, alpha=.75, label=lb)
        ax3.plot(osm, sl * np.array(osm) + ic, "--", color=c, lw=1.2, alpha=.7)
    ax3.set_xlabel("Theoretical Quantiles", fontsize=8)
    ax3.set_ylabel("Sample Quantiles", fontsize=8)
    ax3.set_title("Normal Q-Q Plot by Group", fontsize=9, fontweight="bold")
    ax3.legend(fontsize=7, framealpha=.7)

    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# ONE-WAY ANOVA / KRUSKAL-WALLIS (placeholder — to be expanded)
# ══════════════════════════════════════════════════════════════════════════════

def plot_oneway_anova(groups_data, group_labels, dep_var):
    """
    Diagnostic plots for One-Way ANOVA.
    Panel 1: Box plots by group
    Panel 2: Mean ± SE plot (error bar chart)
    Panel 3: Residuals Q-Q plot

    Parameters
    ----------
    groups_data  : list of array-like — one array per group
    group_labels : list of str
    dep_var      : str

    Returns
    -------
    matplotlib.figure.Figure
    """
    groups_data = [np.array(g, dtype=float) for g in groups_data]
    n_groups    = len(groups_data)
    fig, gs     = _new_fig(3)

    # ── Panel 1: Box plots ───────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    bp  = ax1.boxplot(groups_data, patch_artist=True, widths=0.5,
                      medianprops={"color": "white", "linewidth": 2.5},
                      whiskerprops={"color": PAL[0], "linewidth": 1.2},
                      capprops={"color": PAL[0], "linewidth": 1.2},
                      flierprops={"marker": "o", "markersize": 4, "alpha": .7})
    _colors = [PAL[0], PAL[1], PAL[2], PAL[3],
               "#7c3aed", "#0891b2", "#15803d", "#b45309"]
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(_colors[i % len(_colors)])
        patch.set_alpha(0.78)
    ax1.set_xticklabels(group_labels, fontsize=7, rotation=20, ha="right")
    ax1.set_ylabel(dep_var, fontsize=8)
    ax1.set_title("Box Plots by Group", fontsize=9, fontweight="bold")

    # ── Panel 2: Mean ± SE ───────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    means = [g.mean() for g in groups_data]
    sems  = [scipy_stats.sem(g) for g in groups_data]
    xs    = np.arange(n_groups)
    ax2.bar(xs, means, color=PAL[1], alpha=0.72, edgecolor="white",
            linewidth=.8)
    ax2.errorbar(xs, means, yerr=sems, fmt="none",
                 color=PAL[0], capsize=5, lw=1.5)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(group_labels, fontsize=7, rotation=20, ha="right")
    ax2.set_ylabel(f"Mean {dep_var}", fontsize=8)
    ax2.set_title("Mean \u00b1 SE by Group", fontsize=9, fontweight="bold")

    # ── Panel 3: Residuals Q-Q ───────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    all_data  = np.concatenate(groups_data)
    group_idx = np.concatenate([
        np.full(len(g), i) for i, g in enumerate(groups_data)
    ])
    group_means_arr = np.array([groups_data[i].mean()
                                for i in group_idx])
    residuals = all_data - group_means_arr
    _draw_qq(ax3, residuals, color=PAL[1])
    ax3.set_title("Residuals Q-Q Plot", fontsize=9, fontweight="bold")

    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# REPEATED MEASURES ANOVA (placeholder)
# ══════════════════════════════════════════════════════════════════════════════

def plot_repeated_measures(data_wide, time_labels, dep_var):
    """
    Diagnostic plots for Repeated Measures ANOVA.
    Panel 1: Individual trajectory lines
    Panel 2: Mean ± SE over time
    Panel 3: Box plots per time point

    Parameters
    ----------
    data_wide   : 2D array-like (n_subjects × n_timepoints)
    time_labels : list of str
    dep_var     : str

    Returns
    -------
    matplotlib.figure.Figure
    """
    data_wide = np.array(data_wide, dtype=float)
    n_sub, n_time = data_wide.shape
    xs = np.arange(n_time)
    fig, gs = _new_fig(3)

    # ── Panel 1: Individual trajectories ────────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    for i in range(n_sub):
        ax1.plot(xs, data_wide[i, :], "-o", color=PAL[0],
                 alpha=0.25, markersize=3, lw=.8)
    ax1.plot(xs, data_wide.mean(axis=0), "-o", color=PAL[1],
             lw=2.8, markersize=8, label="Group mean", zorder=5)
    ax1.set_xticks(xs)
    ax1.set_xticklabels(time_labels, fontsize=8)
    ax1.set_ylabel(dep_var, fontsize=8)
    ax1.set_title("Individual Trajectories", fontsize=9, fontweight="bold")
    ax1.legend(fontsize=7, framealpha=.7)

    # ── Panel 2: Mean ± SE ───────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    means = data_wide.mean(axis=0)
    sems  = scipy_stats.sem(data_wide, axis=0)
    ax2.plot(xs, means, "-o", color=PAL[1], lw=2, markersize=7)
    ax2.fill_between(xs, means - sems, means + sems,
                     alpha=0.2, color=PAL[1])
    ax2.set_xticks(xs)
    ax2.set_xticklabels(time_labels, fontsize=8)
    ax2.set_ylabel(f"Mean {dep_var}", fontsize=8)
    ax2.set_title("Mean \u00b1 SE Over Time", fontsize=9, fontweight="bold")

    # ── Panel 3: Box plots per time ──────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    ax3.boxplot([data_wide[:, t] for t in range(n_time)],
                patch_artist=True, widths=0.5,
                medianprops={"color": "white", "linewidth": 2},
                boxprops={"facecolor": PAL[1], "alpha": 0.72},
                whiskerprops={"color": PAL[0], "linewidth": 1.2},
                capprops={"color": PAL[0], "linewidth": 1.2},
                flierprops={"marker": "o", "color": PAL[1],
                            "markersize": 4, "alpha": .7})
    ax3.set_xticklabels(time_labels, fontsize=8)
    ax3.set_ylabel(dep_var, fontsize=8)
    ax3.set_title("Box Plots per Time Point", fontsize=9, fontweight="bold")

    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# REGRESSION (placeholder)
# ══════════════════════════════════════════════════════════════════════════════

def plot_regression(x, y, y_pred, residuals, predictor_name, outcome_name):
    """
    Diagnostic plots for Linear Regression.
    Panel 1: Scatter plot with regression line
    Panel 2: Residuals vs Fitted
    Panel 3: Residuals Q-Q plot

    Parameters
    ----------
    x              : array-like — predictor values
    y              : array-like — observed outcome values
    y_pred         : array-like — fitted values
    residuals      : array-like — residuals (y - y_pred)
    predictor_name : str
    outcome_name   : str

    Returns
    -------
    matplotlib.figure.Figure
    """
    x         = np.array(x, dtype=float)
    y         = np.array(y, dtype=float)
    y_pred    = np.array(y_pred, dtype=float)
    residuals = np.array(residuals, dtype=float)
    fig, gs   = _new_fig(3)

    # ── Panel 1: Scatter + regression line ──────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    ax1.scatter(x, y, color=PAL[1], alpha=0.65, s=30,
                edgecolors="white", linewidths=.5, zorder=3)
    sort_idx = np.argsort(x)
    ax1.plot(x[sort_idx], y_pred[sort_idx],
             color=PAL[0], lw=2, alpha=.85)
    ax1.set_xlabel(predictor_name, fontsize=8)
    ax1.set_ylabel(outcome_name, fontsize=8)
    ax1.set_title("Scatter Plot with Regression Line",
                  fontsize=9, fontweight="bold")

    # ── Panel 2: Residuals vs Fitted ─────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    ax2.scatter(y_pred, residuals, color=PAL[1], alpha=0.65, s=30,
                edgecolors="white", linewidths=.5, zorder=3)
    ax2.axhline(0, color=PAL[0], ls="--", lw=1.5, alpha=.7)
    ax2.set_xlabel("Fitted Values", fontsize=8)
    ax2.set_ylabel("Residuals", fontsize=8)
    ax2.set_title("Residuals vs. Fitted", fontsize=9, fontweight="bold")

    # ── Panel 3: Residuals Q-Q ───────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    _draw_qq(ax3, residuals, color=PAL[1])
    ax3.set_title("Residuals Q-Q Plot", fontsize=9, fontweight="bold")

    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# ANCOVA (placeholder)
# ══════════════════════════════════════════════════════════════════════════════

def plot_ancova(groups_data, covariate_data, group_labels,
                dep_var, covariate_name):
    """
    Diagnostic plots for ANCOVA.
    Panel 1: Scatter of covariate vs outcome by group
    Panel 2: Adjusted means with error bars
    Panel 3: Residuals Q-Q plot

    Parameters
    ----------
    groups_data    : list of array-like — outcome per group
    covariate_data : list of array-like — covariate per group
    group_labels   : list of str
    dep_var        : str
    covariate_name : str

    Returns
    -------
    matplotlib.figure.Figure
    """
    groups_data    = [np.array(g, dtype=float) for g in groups_data]
    covariate_data = [np.array(c, dtype=float) for c in covariate_data]
    fig, gs        = _new_fig(3)
    _colors        = [PAL[0], PAL[1], PAL[2], PAL[3]]

    # ── Panel 1: Scatter by group ────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0]); _style_ax(ax1)
    for i, (gd, cd, lb) in enumerate(
            zip(groups_data, covariate_data, group_labels)):
        c = _colors[i % len(_colors)]
        ax1.scatter(cd, gd, color=c, alpha=0.65, s=30,
                    edgecolors="white", linewidths=.5, label=lb, zorder=3)
        # Regression line per group
        if len(cd) > 1:
            m, b = np.polyfit(cd, gd, 1)
            xs_line = np.linspace(cd.min(), cd.max(), 100)
            ax1.plot(xs_line, m * xs_line + b, color=c, lw=1.5,
                     alpha=.7, ls="--")
    ax1.set_xlabel(covariate_name, fontsize=8)
    ax1.set_ylabel(dep_var, fontsize=8)
    ax1.set_title(f"{dep_var} vs. {covariate_name} by Group",
                  fontsize=9, fontweight="bold")
    ax1.legend(fontsize=7, framealpha=.7)

    # ── Panel 2: Unadjusted means ± SE ──────────────────────────────────────
    ax2 = fig.add_subplot(gs[1]); _style_ax(ax2)
    means = [g.mean() for g in groups_data]
    sems  = [scipy_stats.sem(g) for g in groups_data]
    xs    = np.arange(len(groups_data))
    ax2.bar(xs, means, color=PAL[1], alpha=0.72, edgecolor="white",
            linewidth=.8)
    ax2.errorbar(xs, means, yerr=sems, fmt="none",
                 color=PAL[0], capsize=5, lw=1.5)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(group_labels, fontsize=8)
    ax2.set_ylabel(f"Mean {dep_var}", fontsize=8)
    ax2.set_title("Unadjusted Group Means \u00b1 SE",
                  fontsize=9, fontweight="bold")

    # ── Panel 3: Residuals Q-Q ───────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2]); _style_ax(ax3)
    all_d = np.concatenate(groups_data)
    all_c = np.concatenate(covariate_data)
    if len(all_d) > 2:
        m_all, b_all = np.polyfit(all_c, all_d, 1)
        resid = all_d - (m_all * all_c + b_all)
        _draw_qq(ax3, resid, color=PAL[1])
    ax3.set_title("Residuals Q-Q Plot", fontsize=9, fontweight="bold")

    plt.tight_layout()
    return fig
