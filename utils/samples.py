"""
utils/samples.py
================
Built-in sample datasets for all statistical tests.
Each entry contains:
  - csv       : raw CSV string
  - desc      : HTML description of what the test does (uses <b> for bold)
  - note      : column requirements for the user
  - use_when  : academic-English guidance on when to use this test
  - assumptions: list of key statistical assumptions
  - nonparam  : non-parametric equivalent test name
"""


# ══════════════════════════════════════════════════════════════════════════════
# T-TEST FAMILY
# ══════════════════════════════════════════════════════════════════════════════

SAMPLES = {

    # ── One-Sample T-Test ──────────────────────────────────────────────────────
    "One-Sample T-Test": {
        "csv": (
            "subject_id,score\n"
            "1,78\n2,85\n3,72\n4,90\n5,68\n6,88\n7,75\n8,82\n9,79\n10,93\n"
            "11,71\n12,84\n13,76\n14,89\n15,80"
        ),
        "desc": (
            "Test whether the mean of a <b>single continuous variable</b> "
            "significantly differs from a known or hypothesised population "
            "mean (\u03bc\u2080)."
        ),
        "note": (
            "One numeric column required. "
            "Set the hypothesised population mean (\u03bc\u2080) before running."
        ),
        "use_when": (
            "Use the One-Sample T-Test when you have one continuous dependent "
            "variable measured on a single group and wish to determine whether "
            "the sample mean deviates significantly from a pre-specified "
            "reference value (e.g., a national norm, a theoretical threshold, "
            "or a population mean reported in prior research)."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Observations are independent of one another.",
            "The dependent variable is approximately normally distributed "
            "(assessed via Shapiro-Wilk for n < 50; "
            "Kolmogorov-Smirnov with Lilliefors correction for n \u2265 50).",
        ],
        "nonparam": "Wilcoxon Signed-Rank Test",
        "nonparam_when": (
            "Use the Wilcoxon Signed-Rank Test when the normality assumption "
            "is violated."
        ),
    },

    # ── Paired-Sample T-Test ───────────────────────────────────────────────────
    "Paired-Sample T-Test": {
        "csv": (
            "subject_id,pre_score,post_score\n"
            "1,65,72\n2,70,78\n3,58,65\n4,75,80\n5,62,70\n"
            "6,68,74\n7,72,79\n8,60,68\n9,74,81\n10,66,73\n"
            "11,71,76\n12,63,69\n13,69,75\n14,73,80\n15,67,72"
        ),
        "desc": (
            "Test whether the <b>mean difference</b> between two related "
            "measurements (e.g., pre-test and post-test scores from the "
            "same participants) is significantly different from zero."
        ),
        "note": (
            "Two numeric columns required: "
            "Variable 1 (pre / Time 1) and Variable 2 (post / Time 2). "
            "Both columns must contain scores from the same subjects."
        ),
        "use_when": (
            "Use the Paired-Sample T-Test (also known as the Dependent "
            "Samples T-Test or Repeated Measures T-Test) when the same "
            "participants are measured under two conditions or at two time "
            "points, and you wish to determine whether the mean change "
            "is statistically significant."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Observations are paired — each score in Variable 1 corresponds "
            "to a score in Variable 2 from the same subject.",
            "The differences (Variable 1 \u2212 Variable 2) are approximately "
            "normally distributed "
            "(assessed via Shapiro-Wilk for n < 50; "
            "Kolmogorov-Smirnov with Lilliefors correction for n \u2265 50).",
        ],
        "nonparam": "Wilcoxon Signed-Rank Test",
        "nonparam_when": (
            "Use the Wilcoxon Signed-Rank Test when the normality of "
            "differences assumption is violated."
        ),
    },

    # ── Independent-Sample T-Test ──────────────────────────────────────────────
    "Independent-Sample T-Test": {
        "csv": (
            "subject_id,group,score\n"
            "1,Control,58\n2,Control,62\n3,Control,55\n4,Control,67\n"
            "5,Control,60\n6,Control,63\n7,Control,57\n8,Control,65\n"
            "9,Treatment,72\n10,Treatment,78\n11,Treatment,70\n"
            "12,Treatment,81\n13,Treatment,75\n14,Treatment,77\n"
            "15,Treatment,73\n16,Treatment,79"
        ),
        "desc": (
            "Test whether the means of a <b>continuous dependent variable</b> "
            "differ significantly between <b>two independent groups</b>."
        ),
        "note": (
            "One categorical grouping column and one numeric outcome column "
            "required. The grouping column must contain exactly two distinct "
            "group labels."
        ),
        "use_when": (
            "Use the Independent-Sample T-Test when you have two separate, "
            "unrelated groups (e.g., control vs. treatment, male vs. female) "
            "and wish to determine whether their population means on a "
            "continuous outcome variable are significantly different."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "The two groups are independent — participants belong to one "
            "group only.",
            "The dependent variable is approximately normally distributed "
            "within each group, assessed based on total N: "
            "Shapiro-Wilk for total N < 50; "
            "Kolmogorov-Smirnov with Lilliefors correction for total N \u2265 50.",
            "Homogeneity of variance across groups "
            "(assessed via Levene\u2019s test, center = mean). "
            "If violated, the Welch correction is applied automatically.",
        ],
        "nonparam": "Mann-Whitney U Test",
        "nonparam_when": (
            "Use the Mann-Whitney U Test when the normality assumption is "
            "violated in one or both groups."
        ),
    },

    # ── One-Way ANOVA ──────────────────────────────────────────────────────────
    "One-Way ANOVA": {
        "csv": (
            "subject_id,group,score\n"
            "1,Group_A,55\n2,Group_A,60\n3,Group_A,58\n4,Group_A,62\n"
            "5,Group_A,57\n6,Group_B,70\n7,Group_B,75\n8,Group_B,72\n"
            "9,Group_B,68\n10,Group_B,74\n11,Group_C,80\n12,Group_C,85\n"
            "13,Group_C,82\n14,Group_C,78\n15,Group_C,84"
        ),
        "desc": (
            "Test whether the means of a <b>continuous dependent variable</b> "
            "differ significantly across <b>three or more independent groups</b>."
        ),
        "note": (
            "One categorical grouping column and one numeric outcome column "
            "required. The grouping column must contain three or more "
            "distinct group labels."
        ),
        "use_when": (
            "Use One-Way ANOVA when you have one continuous dependent variable "
            "and one categorical independent variable (factor) with three or "
            "more levels, and wish to test for overall mean differences. "
            "If significant, follow up with post-hoc tests "
            "(e.g., Tukey HSD, Bonferroni) to identify which pairs differ."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Groups are independent of one another.",
            "The dependent variable is approximately normally distributed "
            "within each group.",
            "Homogeneity of variance across groups "
            "(assessed via Levene\u2019s test).",
        ],
        "nonparam": "Kruskal-Wallis Test",
        "nonparam_when": (
            "Use the Kruskal-Wallis Test when normality or homogeneity of "
            "variance assumptions are violated."
        ),
    },

    # ── Factorial ANOVA ────────────────────────────────────────────────────────
    "Factorial ANOVA": {
        "csv": (
            "subject_id,factor_a,factor_b,score\n"
            "1,A1,B1,54.5\n2,A1,B1,58.7\n3,A1,B1,47.8\n"
            "4,A1,B1,51.7\n5,A1,B1,54.5\n"
            "6,A1,B2,73.7\n7,A1,B2,70.0\n8,A1,B2,62.0\n"
            "9,A1,B2,66.8\n10,A1,B2,64.0\n"
            "11,A2,B1,61.8\n12,A2,B1,62.9\n13,A2,B1,61.7\n"
            "14,A2,B1,66.6\n15,A2,B1,67.8\n"
            "16,A2,B2,71.1\n17,A2,B2,85.3\n18,A2,B2,80.2\n"
            "19,A2,B2,79.2\n20,A2,B2,78.4"
        ),
        "desc": (
            "Test the main effects of <b>two or more categorical factors</b> "
            "and their <b>interaction effect</b> on a continuous dependent variable."
        ),
        "note": (
            "Two categorical factor columns and one numeric outcome column "
            "required. Each factor must have two or more levels."
        ),
        "use_when": (
            "Use Factorial ANOVA (also known as Two-Way ANOVA or N-Way ANOVA) "
            "when you have two or more categorical independent variables "
            "(factors) and wish to examine their individual main effects and "
            "their combined interaction effect on a continuous outcome. "
            "The interaction term reveals whether the effect of one factor "
            "depends on the level of another."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Groups are independent of one another.",
            "The dependent variable is approximately normally distributed "
            "within each cell (combination of factor levels).",
            "Homogeneity of variance across all cells "
            "(assessed via Levene\u2019s test).",
        ],
        "nonparam": "Scheirer-Ray-Hare Test",
        "nonparam_when": (
            "Use the Scheirer-Ray-Hare Test as a non-parametric alternative "
            "when assumptions are violated."
        ),
    },

    # ── Repeated Measures ANOVA ────────────────────────────────────────────────
    "Repeated Measures ANOVA": {
        "csv": (
            "subject_id,time_1,time_2,time_3\n"
            "1,54.1,69.0,69.6\n"
            "2,61.4,70.3,75.1\n"
            "3,43.3,52.9,61.7\n"
            "4,52.4,61.8,64.8\n"
            "5,57.7,64.2,74.4\n"
            "6,69.8,84.5,91.0\n"
            "7,72.3,76.4,83.2\n"
            "8,56.5,63.5,69.4\n"
            "9,63.6,74.7,78.9\n"
            "10,58.7,66.5,76.4"
        ),
        "desc": (
            "Test whether a <b>continuous dependent variable</b> changes "
            "significantly across <b>three or more time points or conditions</b> "
            "measured on the same participants."
        ),
        "note": (
            "Wide-format data required: one column per time point/condition, "
            "one row per subject. All measurement columns must be numeric."
        ),
        "use_when": (
            "Use Repeated Measures ANOVA when the same participants are "
            "measured on the same continuous outcome variable at three or more "
            "time points or under three or more conditions. This design "
            "controls for individual differences and is more statistically "
            "powerful than between-subjects designs."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Observations are from the same subjects across all time points.",
            "The dependent variable is approximately normally distributed "
            "at each time point.",
            "Sphericity: the variances of the differences between all pairs "
            "of time points are equal (assessed via Mauchly\u2019s test). "
            "If violated, Greenhouse-Geisser or Huynh-Feldt correction "
            "is applied automatically.",
        ],
        "nonparam": "Friedman Test",
        "nonparam_when": (
            "Use the Friedman Test when normality or sphericity assumptions "
            "are substantially violated."
        ),
    },

    # ── Mixed ANOVA ────────────────────────────────────────────────────────────
    "Mixed ANOVA": {
        "csv": (
            "subject_id,group,time_1,time_2,time_3\n"
            "1,Control,66.8,69.6,64.6\n"
            "2,Control,59.9,52.5,63.0\n"
            "3,Control,49.1,46.9,57.5\n"
            "4,Control,50.1,57.1,58.1\n"
            "5,Control,61.3,56.0,55.8\n"
            "6,Control,55.9,59.5,61.2\n"
            "7,Control,37.1,32.1,37.5\n"
            "8,Treatment,42.5,54.4,56.7\n"
            "9,Treatment,58.3,61.2,70.3\n"
            "10,Treatment,52.9,60.8,70.2\n"
            "11,Treatment,56.8,65.0,82.6\n"
            "12,Treatment,61.5,73.0,81.0\n"
            "13,Treatment,45.9,51.2,57.8\n"
            "14,Treatment,49.4,53.1,71.0"
        ),
        "desc": (
            "Test the effects of a <b>between-subjects factor</b> (group), "
            "a <b>within-subjects factor</b> (time), and their "
            "<b>interaction</b> on a continuous dependent variable."
        ),
        "note": (
            "One categorical grouping column (between-subjects factor) and "
            "multiple numeric columns representing repeated measurements "
            "(within-subjects factor) required."
        ),
        "use_when": (
            "Use Mixed ANOVA (also known as Split-Plot ANOVA) when your design "
            "includes both a between-subjects factor (e.g., treatment vs. "
            "control group) and a within-subjects factor (e.g., measurements "
            "at multiple time points). The critical result is typically the "
            "interaction effect, which indicates whether the trajectory of "
            "change over time differs between groups."
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Between-subjects groups are independent.",
            "Within-subjects measurements come from the same participants.",
            "The dependent variable is approximately normally distributed "
            "within each cell.",
            "Homogeneity of variance across between-subjects groups "
            "(Levene\u2019s test).",
            "Sphericity of the within-subjects factor "
            "(Mauchly\u2019s test; corrections applied if violated).",
        ],
        "nonparam": "Aligned Ranks Transform (ART) ANOVA",
        "nonparam_when": (
            "Use the Aligned Ranks Transform ANOVA when normality assumptions "
            "are substantially violated."
        ),
    },

    # ── One-Way ANCOVA ─────────────────────────────────────────────────────────
    "One-Way ANCOVA": {
        "csv": (
            "subject_id,group,pre_score,post_score\n"
            "1,Control,51.0,63.1\n2,Control,47.2,71.0\n3,Control,51.9,65.9\n"
            "4,Control,57.1,64.3\n5,Control,46.6,66.6\n6,Control,46.6,58.4\n"
            "7,Control,57.5,69.6\n8,Control,52.6,58.5\n9,Control,45.2,57.3\n"
            "10,Control,51.3,66.4\n"
            "11,Training_A,47.2,74.6\n12,Training_A,47.2,72.3\n"
            "13,Training_A,51.5,73.3\n14,Training_A,38.5,66.1\n"
            "15,Training_A,39.7,61.9\n16,Training_A,46.6,68.4\n"
            "17,Training_A,43.9,68.1\n18,Training_A,51.9,78.2\n"
            "19,Training_A,44.6,71.7\n20,Training_A,41.5,61.7\n"
            "21,Training_B,57.8,85.2\n22,Training_B,47.6,77.3\n"
            "23,Training_B,49.4,77.0\n24,Training_B,40.5,77.7\n"
            "25,Training_B,45.7,82.0\n26,Training_B,49.7,83.6\n"
            "27,Training_B,42.1,72.7\n28,Training_B,51.3,79.4\n"
            "29,Training_B,45.4,79.0\n30,Training_B,47.2,82.5"
        ),
        "desc": (
            "Test group mean differences on a <b>continuous dependent variable</b> "
            "while <b>statistically controlling for one or more covariates</b>."
        ),
        "note": (
            "One categorical grouping column, one numeric covariate column, "
            "and one numeric outcome column required."
        ),
        "use_when": (
            "Use One-Way ANCOVA when you wish to compare group means on a "
            "continuous outcome while removing the influence of one or more "
            "continuous covariates (confounding variables). ANCOVA reduces "
            "error variance and increases statistical power by accounting for "
            "pre-existing differences between groups."
        ),
        "assumptions": [
            "The dependent variable and covariate are continuous.",
            "Groups are independent of one another.",
            "The covariate is linearly related to the dependent variable "
            "within each group (tested via scatterplot and correlation).",
            "Homogeneity of regression slopes: the relationship between the "
            "covariate and outcome does not differ across groups.",
            "The dependent variable is approximately normally distributed "
            "within each group after controlling for the covariate.",
            "Homogeneity of variance across groups (Levene\u2019s test).",
        ],
        "nonparam": "Quade Test / Rank ANCOVA",
        "nonparam_when": (
            "Use the Quade Test or Rank ANCOVA when normality assumptions "
            "are violated."
        ),
    },

    # ── Factorial ANCOVA ───────────────────────────────────────────────────────
    "Factorial ANCOVA": {
        "csv": (
            "subject_id,method,feedback,pre_score,achievement\n"
            "1,A1,B1,46.2,49.4\n2,A1,B1,48.5,51.9\n3,A1,B1,41.1,56.0\n"
            "4,A1,B1,40.4,52.8\n5,A1,B1,56.5,55.0\n6,A1,B1,60.8,61.9\n"
            "7,A1,B2,49.4,60.3\n8,A1,B2,58.0,68.1\n9,A1,B2,52.9,57.6\n"
            "10,A1,B2,44.8,56.3\n11,A1,B2,52.9,59.2\n12,A1,B2,62.3,57.6\n"
            "13,A2,B1,49.7,63.4\n14,A2,B1,62.5,68.3\n15,A2,B1,29.0,53.6\n"
            "16,A2,B1,36.2,52.7\n17,A2,B1,47.4,62.6\n18,A2,B1,58.6,64.5\n"
            "19,A2,B2,42.9,72.6\n20,A2,B2,56.3,76.2\n21,A2,B2,48.3,73.2\n"
            "22,A2,B2,44.6,71.5\n23,A2,B2,50.6,74.1\n24,A2,B2,57.9,78.4"
        ),
        "desc": (
            "Test the main effects of <b>two or more factors</b> and their "
            "<b>interaction</b> on a continuous dependent variable while "
            "<b>controlling for covariates</b>."
        ),
        "note": (
            "Two categorical factor columns, one or more numeric covariate "
            "columns, and one numeric outcome column required."
        ),
        "use_when": (
            "Use Factorial ANCOVA when you have a factorial design (multiple "
            "categorical factors) and wish to control for the influence of "
            "one or more continuous covariates. This combines the logic of "
            "Factorial ANOVA and ANCOVA."
        ),
        "assumptions": [
            "The dependent variable and covariate(s) are continuous.",
            "Groups are independent of one another.",
            "Linear relationship between covariate(s) and dependent variable.",
            "Homogeneity of regression slopes across all cells.",
            "Normality of residuals within each cell.",
            "Homogeneity of variance (Levene\u2019s test).",
        ],
        "nonparam": "Rank-based ANCOVA",
        "nonparam_when": (
            "Use rank-based ANCOVA when normality assumptions are violated."
        ),
    },

    # ── Repeated Measures ANCOVA ───────────────────────────────────────────────
    "Repeated Measures ANCOVA": {
        "csv": (
            "subject_id,age,pre_test,mid_test,post_test\n"
            "1,26,64.0,66.1,80.2\n2,39,67.3,69.8,85.0\n3,34,72.5,76.9,91.9\n"
            "4,30,71.7,78.9,84.4\n5,27,50.9,68.3,78.6\n6,40,70.0,75.9,84.1\n"
            "7,26,61.5,63.8,73.0\n8,38,65.6,71.4,76.2\n9,42,60.2,72.4,73.2\n"
            "10,30,71.4,78.6,72.2\n11,30,63.9,72.6,82.2\n12,43,69.7,67.9,78.4\n"
            "13,40,69.1,63.1,84.4\n14,23,66.1,63.7,83.4\n15,27,61.6,71.0,79.2\n"
            "16,43,67.8,76.5,85.9\n17,22,62.1,72.3,72.1\n18,41,70.6,65.1,81.7\n"
            "19,40,66.3,76.8,89.3\n20,21,61.1,68.4,70.7"
        ),
        "desc": (
            "Examine how scores change across <b>three time points</b> "
            "while statistically controlling for <b>age</b> as a covariate."
        ),
        "note": (
            "Two or more numeric time-point columns and one numeric covariate "
            "column (between-subjects) required. Each row is one subject."
        ),
        "use_when": (
            "Use Repeated Measures ANCOVA when the same participants are "
            "measured at multiple time points and you wish to control for "
            "a between-subjects covariate (e.g., age, baseline score)."
        ),
        "assumptions": [
            "The dependent variable is continuous and measured repeatedly.",
            "The covariate is continuous and measured once per subject.",
            "The covariate is linearly related to the dependent variable.",
            "Homogeneity of regression slopes across time points.",
            "Normality of residuals within each time point.",
            "Sphericity (tested with Mauchly's test; GG correction applied).",
        ],
        "nonparam": "Friedman Test (without covariate adjustment)",
        "nonparam_when": "Use Friedman Test when normality is severely violated.",
    },

    # ── Mixed ANCOVA ───────────────────────────────────────────────────────────
    "Mixed ANCOVA": {
        "csv": (
            "subject_id,group,baseline,time1,time2,time3\n"
            "1,Control,57.6,82.0,67.7,70.7\n2,Control,63.8,79.1,81.6,78.2\n"
            "3,Control,53.7,72.9,69.1,66.2\n4,Control,36.5,71.3,64.9,64.9\n"
            "5,Control,52.6,67.1,74.6,73.0\n6,Control,49.4,67.9,63.1,81.2\n"
            "7,Control,53.7,62.2,69.1,73.9\n8,Control,55.9,70.4,72.9,76.1\n"
            "9,Control,43.8,73.9,65.1,74.2\n10,Control,43.2,66.7,65.0,74.2\n"
            "11,Treatment,46.8,63.4,84.6,87.2\n12,Treatment,40.3,63.9,82.1,77.9\n"
            "13,Treatment,49.2,73.1,76.1,92.5\n14,Treatment,47.1,66.6,77.6,89.7\n"
            "15,Treatment,69.1,79.8,92.1,87.1\n16,Treatment,39.8,58.1,67.4,80.8\n"
            "17,Treatment,41.7,61.3,78.6,90.8\n18,Treatment,51.4,66.4,91.3,92.1\n"
            "19,Treatment,55.0,62.6,92.3,85.2\n20,Treatment,66.3,91.6,72.2,91.3"
        ),
        "desc": (
            "Compare <b>Control vs Treatment</b> groups across three time points "
            "while controlling for <b>baseline score</b>."
        ),
        "note": (
            "One between-subjects factor column, two or more time-point columns, "
            "and one covariate column required."
        ),
        "use_when": (
            "Use Mixed ANCOVA when you have both a between-subjects factor "
            "(e.g., group) and a within-subjects factor (e.g., time), and you "
            "wish to control for a continuous covariate."
        ),
        "assumptions": [
            "Between-subjects factor is categorical; time points are continuous.",
            "The covariate is linearly related to the dependent variable.",
            "Homogeneity of regression slopes.",
            "Normality of residuals.",
            "Homogeneity of variance across between-subjects groups.",
            "Sphericity for the within-subjects factor.",
        ],
        "nonparam": "Aligned Rank Transform ANOVA (ART-ANOVA)",
        "nonparam_when": "Use ART-ANOVA when normality assumptions are violated.",
    },

    # ── MANCOVA ────────────────────────────────────────────────────────────────
    "MANCOVA": {
        "csv": (
            "subject_id,group,iq,reading_score,math_score\n"
            "1,Method_A,98.3,59.0,43.3\n2,Method_A,107.4,46.7,44.4\n"
            "3,Method_A,115.0,47.0,36.0\n4,Method_A,100.8,57.9,46.3\n"
            "5,Method_A,114.0,57.9,59.6\n6,Method_A,110.5,74.1,48.6\n"
            "7,Method_A,102.5,41.4,53.1\n8,Method_A,82.7,50.7,35.6\n"
            "9,Method_A,87.7,49.1,35.4\n10,Method_A,108.9,52.6,45.2\n"
            "11,Method_B,81.5,57.7,40.6\n12,Method_B,103.4,56.6,45.7\n"
            "13,Method_B,114.0,45.9,60.1\n14,Method_B,103.8,51.0,66.5\n"
            "15,Method_B,94.8,64.3,46.9\n16,Method_B,91.8,62.2,38.9\n"
            "17,Method_B,111.8,56.3,60.9\n18,Method_B,107.7,61.5,45.1\n"
            "19,Method_B,98.6,75.1,44.3\n20,Method_B,114.8,59.5,60.6\n"
            "21,Method_C,111.2,64.7,60.0\n22,Method_C,122.5,69.0,59.5\n"
            "23,Method_C,107.8,68.2,60.7\n24,Method_C,99.0,59.3,54.9\n"
            "25,Method_C,99.3,66.1,71.0\n26,Method_C,77.8,42.8,47.1\n"
            "27,Method_C,102.8,65.1,52.4\n28,Method_C,100.8,62.6,55.0\n"
            "29,Method_C,85.0,56.7,50.9\n30,Method_C,100.7,58.8,62.4"
        ),
        "desc": (
            "Test whether <b>three teaching methods</b> (A, B, C) differ on "
            "<b>reading and math scores</b> simultaneously, after controlling "
            "for <b>IQ</b> as a covariate."
        ),
        "note": (
            "One categorical factor column, one numeric covariate column, and "
            "two or more numeric dependent variable columns required."
        ),
        "use_when": (
            "Use MANCOVA when you have multiple continuous dependent variables "
            "and wish to compare groups while controlling for a covariate. "
            "It protects against inflated Type I error from multiple ANCOVAs."
        ),
        "assumptions": [
            "All dependent variables and the covariate are continuous.",
            "Groups are independent.",
            "Multivariate normality of residuals.",
            "Homogeneity of variance-covariance matrices (Box's M test).",
            "No multicollinearity among dependent variables.",
            "Linear relationships between the covariate and each DV.",
            "Homogeneity of regression slopes across groups.",
        ],
        "nonparam": "Nonparametric MANCOVA (rank-based)",
        "nonparam_when": "Use rank-based MANCOVA when multivariate normality is violated.",
    },

    # ── Linear Regression ──────────────────────────────────────────────────────
    "Linear Regression": {
        "csv": (
            "subject_id,exam_score,study_hours\n"
            "1,78.0,11.2\n2,74.0,8.4\n3,79.4,9.5\n4,53.2,3.4\n5,51.4,2.9\n"
            "6,76.7,9.9\n7,55.2,5.3\n8,68.3,7.4\n9,43.5,4.4\n10,83.8,7.5\n"
            "11,59.8,6.0\n12,74.9,9.2\n13,78.1,10.4\n14,75.2,7.9\n15,52.4,5.0\n"
            "16,49.2,4.8\n17,81.0,9.1\n18,65.7,6.2\n19,44.5,2.6\n20,87.7,9.5"
        ),
        "desc": (
            "Predict <b>exam scores</b> from study hours. "
            "Demonstrates a clear <b>linear relationship</b> with realistic scatter."
        ),
        "note": (
            "One numeric predictor column and one numeric outcome column required. "
            "For multiple predictors, use Multiple Regression."
        ),
        "use_when": (
            "Use Simple Linear Regression when you wish to model the linear "
            "relationship between one continuous predictor (independent "
            "variable) and one continuous outcome (dependent variable), "
            "and to predict outcome values from predictor values."
        ),
        "assumptions": [
            "Both variables are continuous (interval or ratio scale).",
            "The relationship between predictor and outcome is linear.",
            "Residuals are approximately normally distributed.",
            "Homoscedasticity: residuals have constant variance across "
            "fitted values.",
            "Observations are independent.",
            "No influential outliers (assessed via Cook\u2019s Distance).",
        ],
        "nonparam": "Spearman Rank Correlation / Theil-Sen Estimator",
        "nonparam_when": (
            "Use Spearman correlation when normality or linearity assumptions "
            "are violated."
        ),
    },

    # ── Multiple Regression ────────────────────────────────────────────────────
    "Multiple Regression": {
        "csv": (
            "subject_id,study_hours,anxiety_score,sleep_hours,exam_score\n"
            "1,9.0,3.6,4.6,81.0\n2,4.9,3.9,8.1,77.7\n3,4.3,2.8,7.0,63.5\n"
            "4,7.5,3.3,6.7,73.2\n5,9.2,6.0,5.7,68.0\n6,6.2,1.7,5.5,76.0\n"
            "7,11.8,4.5,6.1,88.6\n8,8.8,4.4,7.4,87.6\n9,6.8,4.9,8.4,76.1\n"
            "10,5.9,4.4,6.6,65.7\n11,5.4,3.5,7.3,65.8\n12,9.3,4.4,6.9,84.2\n"
            "13,6.4,8.1,7.1,62.4\n14,2.6,8.6,7.4,48.4\n15,6.0,5.0,8.2,77.1\n"
            "16,9.4,6.0,4.4,67.4\n17,3.8,1.9,7.8,68.8\n18,3.8,3.5,5.2,65.1\n"
            "19,7.3,4.3,5.0,64.1\n20,7.3,7.9,6.9,68.1\n21,8.3,3.0,4.5,66.0\n"
            "22,10.5,4.9,8.4,82.8\n23,9.2,8.9,7.1,72.0\n24,8.1,5.2,7.6,64.2\n"
            "25,9.2,5.9,4.1,66.6"
        ),
        "desc": (
            "Predict <b>exam scores</b> from study hours, anxiety level, "
            "and sleep hours. Three independent predictors with low intercorrelation "
            "(VIF\u2009&lt;\u20092) demonstrate clean <b>Multiple Regression</b>."
        ),
        "note": (
            "Two or more numeric predictor columns and one numeric outcome column "
            "required. Dichotomous variables (0/1) may also be used as predictors "
            "(dummy coding). Ensure predictors are not highly intercorrelated "
            "(VIF\u2009&lt;\u200910)."
        ),
        "use_when": (
            "Use Multiple Regression when you wish to predict a continuous "
            "outcome from two or more predictors simultaneously, to control "
            "for confounders, or to assess the relative importance of "
            "each predictor while holding others constant."
        ),
        "assumptions": [
            "The outcome variable is continuous.",
            "All predictors are continuous or dichotomous (dummy-coded).",
            "Linear relationships between each predictor and the outcome.",
            "Residuals are approximately normally distributed.",
            "Homoscedasticity of residuals.",
            "No multicollinearity: predictors are not highly intercorrelated "
            "(assessed via VIF; VIF > 10 indicates problematic multicollinearity).",
            "Observations are independent.",
            "No influential outliers (Cook\u2019s Distance).",
        ],
        "nonparam": "Robust Regression / Quantile Regression",
        "nonparam_when": (
            "Use robust or quantile regression when normality or "
            "homoscedasticity assumptions are substantially violated."
        ),
    },

    # ── Bivariate Correlation ─────────────────────────────────────
    "Bivariate Correlation": {
        "csv": (
            "subject_id,hours_studied,motivation,anxiety_level,exam_score\n"
            "1,9.3,7.3,6.5,79.6\n2,10.6,8.0,4.5,91.0\n3,9.5,8.4,5.0,81.0\n4,4.9,4.8,7.7,48.8\n5,3.9,5.4,7.5,48.1\n"
            "6,7.1,6.7,6.4,65.4\n7,8.9,8.1,3.3,83.8\n8,8.1,7.4,4.9,74.7\n9,11.0,10.0,6.2,90.9\n10,8.7,6.3,4.6,75.4\n"
            "11,8.4,9.0,3.8,84.4\n12,5.4,5.1,3.5,57.1\n13,4.6,3.8,3.7,51.1\n14,10.3,9.9,3.7,93.3\n15,7.1,5.9,4.1,67.3\n"
            "16,8.8,6.8,7.3,74.5\n17,4.0,2.9,3.4,46.1\n18,6.0,2.9,6.8,54.3\n19,4.2,6.0,5.8,54.3\n20,5.3,3.9,5.3,49.2\n"
            "21,9.0,8.7,3.3,79.2\n22,3.7,7.6,4.1,57.4\n23,5.8,5.7,8.9,64.8\n24,7.4,5.0,5.2,67.7\n25,5.5,6.4,6.1,58.8"
        ),
        "desc": (
            "Assess the <b>strength and direction</b> of the relationship "
            "between two or more continuous variables. The app automatically "
            "selects <b>Pearson</b>, <b>Spearman</b>, or <b>Kendall\u2019s tau-b</b> "
            "based on normality and linearity."
        ),
        "note": (
            "Two or more numeric columns required. Each pair of variables is "
            "correlated; the appropriate coefficient is recommended automatically."
        ),
        "use_when": (
            "Use bivariate correlation when you wish to quantify the degree of "
            "association between two continuous variables without designating "
            "one as a predictor and the other as an outcome. Pearson is used "
            "when both variables are normally distributed and linearly related; "
            "Spearman or Kendall\u2019s tau-b are used otherwise."
        ),
        "assumptions": [
            "Variables are continuous (interval or ratio scale) or ordinal "
            "(for Spearman / Kendall).",
            "Observations are independent (each row is one case).",
            "For Pearson: both variables are approximately normally distributed "
            "and the relationship is linear (assessed automatically).",
            "For Spearman / Kendall: the relationship is monotonic.",
        ],
        "nonparam": "Spearman\u2019s rho / Kendall\u2019s tau-b",
        "nonparam_when": (
            "Spearman or Kendall\u2019s tau-b is recommended automatically when "
            "the normality or linearity assumption is violated."
        ),
    },

    # ── Inter-Rater Agreement — Dichotomous (2 raters) ──────────────────────
    "IRAR Dichotomous": {
        "csv": (
            "student_id,Rater_A,Rater_B\n"
            "1,1,0\n2,0,1\n3,1,1\n4,1,1\n5,1,0\n"
            "6,1,1\n7,1,1\n8,1,0\n9,0,0\n10,1,1\n"
            "11,1,1\n12,1,1\n13,0,1\n14,1,1\n15,1,1\n"
            "16,1,1\n17,0,1\n18,1,1\n19,1,0\n20,1,1\n"
            "21,0,0\n22,1,0\n23,1,1\n24,0,0\n25,1,1"
        ),
        "desc": (
            "Evaluate <b>inter-rater agreement</b> between <b>two raters</b> "
            "scoring student answers as <b>Correct (1) or Incorrect (0)</b>. "
            "Methods computed automatically: Cohen's κ, Gwet's AC1, "
            "Scott's π, Brennan-Prediger, Percentage Agreement, "
            "and Krippendorff's α (nominal metric)."
        ),
        "note": (
            "Two rater columns required (values: 0 or 1). "
            "Each row = one student answer unit. "
            "Context: Two ELT examiners independently marking 25 short-answer items. "
            "Use IRAR Nominal (3 raters) to see Fleiss' κ with three raters."
        ),
        "use_when": (
            "Use when two raters independently classify each unit into one of "
            "two mutually exclusive categories (e.g., Correct/Incorrect, Pass/Fail). "
            "Cohen's κ is the standard index; Gwet's AC1 is preferred when one "
            "category is substantially more frequent (prevalence paradox). "
            "Scott's π and Brennan-Prediger are reported for comparison."
        ),
        "assumptions": [
            "Each unit is rated independently by both raters.",
            "Ratings are mutually exclusive (exactly 2 categories: 0 and 1).",
            "Raters operate under the same operational definition of the categories.",
        ],
        "nonparam": "Gwet's AC1 / Krippendorff's α (nominal metric)",
        "nonparam_when": (
            "Gwet's AC1 is preferred when the prevalence of one category "
            "is very high or very low (prevalence paradox in Cohen's κ)."
        ),
    },

    # ── Inter-Rater Agreement — Nominal (3 raters) ───────────────────────────
    "IRAR Nominal": {
        "csv": (
            "essay_id,Rater_1,Rater_2,Rater_3\n"
            "1,2,2,2\n2,2,2,3\n3,3,3,2\n4,4,4,1\n5,2,2,2\n"
            "6,1,1,1\n7,1,4,3\n8,3,3,3\n9,4,4,4\n10,3,2,2\n"
            "11,1,1,1\n12,3,2,1\n13,1,1,1\n14,1,4,1\n15,1,1,4\n"
            "16,2,2,2\n17,3,4,3\n18,3,3,3\n19,2,1,2\n20,1,4,4"
        ),
        "desc": (
            "Evaluate <b>inter-rater agreement</b> among <b>three raters</b> "
            "classifying grammatical errors in student essays. "
            "Categories: 1=Tense Error, 2=Subject-Verb Agreement, "
            "3=Article Error, 4=Vocabulary Error. "
            "Methods: Fleiss' κ, Gwet's AC1 (multi-rater), "
            "Percentage Agreement, and Krippendorff's α (nominal metric)."
        ),
        "note": (
            "Three or more rater columns required (integer category codes). "
            "Each row = one essay. "
            "Context: Three ELT teachers independently classifying the primary "
            "grammatical error type in 20 student essays. "
            "With k≥3 raters and nominal data, Fleiss' κ and Gwet's AC1 (multi) "
            "are computed instead of Cohen's κ."
        ),
        "use_when": (
            "Use when three or more raters independently assign each unit to "
            "one of several nominal (unordered) categories. "
            "Fleiss' κ is the standard; Gwet's AC1 is more stable when "
            "category distributions are unequal."
        ),
        "assumptions": [
            "Categories are nominal (unordered).",
            "Each unit receives exactly one classification per rater.",
            "Raters operate independently under the same coding scheme.",
        ],
        "nonparam": "Gwet's AC1 (multi-rater) / Krippendorff's α (nominal metric)",
        "nonparam_when": (
            "Gwet's AC1 is preferred over Fleiss' κ when category distributions "
            "are highly skewed."
        ),
    },

    # ── Inter-Rater Agreement — Ordinal (2 raters) ───────────────────────────
    "IRAR Ordinal": {
        "csv": (
            "student_id,Rater_1,Rater_2\n"
            "1,2,4\n2,2,3\n3,2,3\n4,2,2\n5,2,3\n"
            "6,3,3\n7,4,4\n8,2,2\n9,4,3\n10,3,3\n"
            "11,2,3\n12,3,1\n13,3,3\n14,4,3\n15,4,3\n"
            "16,3,4\n17,2,2\n18,4,4\n19,4,4\n20,4,3"
        ),
        "desc": (
            "Evaluate <b>inter-rater agreement</b> between <b>two raters</b> "
            "scoring student essays using an <b>analytic rubric (scale 1–5)</b>. "
            "Methods: Weighted Cohen's κ (quadratic weights), "
            "Gwet's AC2, Percentage Agreement, "
            "and Krippendorff's α (ordinal metric)."
        ),
        "note": (
            "Two rater columns required (integer scores: 1–5). "
            "Each row = one student essay. "
            "Context: Two ELT teachers scoring 20 student writing samples. "
            "Use IRAR Ordinal (3 raters) to see Gwet's AC2 with three raters."
        ),
        "use_when": (
            "Use when two raters assign ordered scores (Likert scales, rubric levels). "
            "Weighted Cohen's κ (quadratic) is standard; Gwet's AC2 is more stable "
            "when score distributions are skewed. Krippendorff's α (ordinal) handles "
            "missing data and any number of raters."
        ),
        "assumptions": [
            "Categories are ordinal (ordered with meaningful rank).",
            "Each unit receives exactly one score per rater.",
            "Raters use the same rubric and scale endpoints.",
        ],
        "nonparam": "Gwet's AC2 / Krippendorff's α (ordinal metric)",
        "nonparam_when": (
            "Gwet's AC2 is preferred when marginal distributions are skewed."
        ),
    },

    # ── Inter-Rater Agreement — Ordinal Multi-rater (3 raters) ───────────────
    "IRAR Ordinal Multi": {
        "csv": (
            "student_id,Rater_1,Rater_2,Rater_3\n"
            "1,2,3,2\n2,3,3,4\n3,2,2,3\n4,4,4,3\n5,3,3,3\n"
            "6,2,3,2\n7,4,5,4\n8,3,3,4\n9,5,4,5\n10,3,3,3\n"
            "11,2,2,2\n12,4,3,4\n13,3,4,3\n14,5,5,4\n15,3,3,4\n"
            "16,2,2,3\n17,4,4,5\n18,3,3,3\n19,4,5,4\n20,2,3,2"
        ),
        "desc": (
            "Evaluate <b>inter-rater agreement</b> among <b>three raters</b> "
            "scoring student oral presentations using a <b>rubric (scale 1–5)</b>. "
            "Methods: Gwet's AC2 (multi-rater, quadratic weights), "
            "Percentage Agreement, and Krippendorff's α (ordinal metric). "
            "Note: Weighted Cohen's κ is only available for exactly 2 raters."
        ),
        "note": (
            "Three rater columns required (integer scores: 1–5). "
            "Each row = one student. "
            "Context: Three ELT teachers scoring 20 students on oral presentation "
            "using a 5-point analytic rubric. "
            "With k≥3 raters and ordinal data, Gwet's AC2 (multi-rater) "
            "and Krippendorff's α are computed."
        ),
        "use_when": (
            "Use when three or more raters assign ordered rubric scores. "
            "Gwet's AC2 (multi-rater) generalises the 2-rater AC2 to "
            "any number of raters using jackknife variance estimation. "
            "Krippendorff's α (ordinal metric) is reported alongside."
        ),
        "assumptions": [
            "Categories are ordinal (1=Very Poor to 5=Excellent).",
            "Each unit receives exactly one score per rater.",
            "Raters are trained on the same rubric.",
            "Scores are treated as ordered discrete values.",
        ],
        "nonparam": "Krippendorff's α (ordinal metric)",
        "nonparam_when": (
            "Krippendorff's α handles missing data and does not require "
            "equal marginal distributions."
        ),
    },

    # ── Inter-Rater Agreement — Interval (4 raters) ──────────────────────────
    "IRAR Interval": {
        "csv": (
            "student_id,Rater_1,Rater_2,Rater_3,Rater_4\n"
            "1,58,59,51,59\n2,74,70,70,72\n3,65,63,58,62\n"
            "4,64,70,66,68\n5,73,78,73,73\n6,84,87,86,97\n"
            "7,70,81,76,73\n8,88,85,83,93\n9,72,68,65,68\n"
            "10,96,93,91,97\n11,86,86,96,88\n12,65,73,59,74\n"
            "13,78,80,72,75\n14,58,72,55,64\n15,69,71,71,72\n"
            "16,75,87,84,86\n17,87,85,85,89\n18,56,67,49,63\n"
            "19,50,57,51,60\n20,65,70,63,73"
        ),
        "desc": (
            "Evaluate <b>inter-rater agreement</b> among <b>four raters</b> "
            "scoring student speaking performance (scale 0–100). "
            "Methods: ICC (all 6 forms: ICC(1,1), ICC(A,1), ICC(C,1), "
            "ICC(1,k), ICC(A,k), ICC(C,k)), "
            "Percentage Agreement, and Krippendorff's α (interval metric). "
            "Note: Lin's CCC is only available for exactly 2 raters — "
            "use IRAR Interval 2-rater to see CCC."
        ),
        "note": (
            "Four rater columns required (continuous scores 0–100). "
            "Each row = one student. "
            "Context: Four ELT examiners scoring 20 students on an oral "
            "proficiency test. With k≥3, ICC(A,k) reports reliability "
            "for the mean of all four raters' scores."
        ),
        "use_when": (
            "Use when three or more raters assign continuous scores. "
            "ICC(A,1) is the primary index for single-rater reliability; "
            "ICC(A,k) applies when you average all raters' scores in practice. "
            "ICC(C) forms assess consistency without penalising systematic bias."
        ),
        "assumptions": [
            "Scores are continuous or approximately interval-level.",
            "Each unit is rated independently by all raters.",
            "For ICC(A): raters are a random sample from a larger pool.",
            "For ICC(C): same fixed raters rate all units.",
        ],
        "nonparam": "Krippendorff's α (interval metric)",
        "nonparam_when": (
            "Krippendorff's α handles missing data and does not require "
            "ANOVA assumptions."
        ),
    },

    # ── Inter-Rater Agreement — Interval 2-rater (ICC + CCC) ─────────────────
    "IRAR Interval 2-rater": {
        "csv": (
            "student_id,Rater_1,Rater_2\n"
            "1,72,68\n2,85,82\n3,61,65\n4,78,75\n5,90,88\n"
            "6,55,60\n7,83,79\n8,67,70\n9,94,91\n10,74,78\n"
            "11,80,77\n12,63,66\n13,88,85\n14,70,73\n15,76,80\n"
            "16,59,62\n17,92,89\n18,68,71\n19,84,87\n20,75,72"
        ),
        "desc": (
            "Evaluate <b>inter-rater agreement</b> between <b>two raters</b> "
            "scoring student writing quality (scale 0–100). "
            "Methods: ICC (all 6 forms), <b>Lin's Concordance Correlation "
            "Coefficient (CCC)</b>, Percentage Agreement, "
            "and Krippendorff's α (interval metric). "
            "Lin's CCC is unique to 2-rater interval/ratio data."
        ),
        "note": (
            "Exactly two rater columns required (continuous scores 0–100). "
            "Each row = one student. "
            "Context: Two senior ELT examiners independently scoring 20 "
            "writing samples. Lin's CCC decomposes agreement into "
            "precision (Pearson r) and accuracy (bias correction C_b)."
        ),
        "use_when": (
            "Use when exactly two raters score continuous data and you want "
            "to separately evaluate precision (how correlated the raters are) "
            "and accuracy (whether they score at the same absolute level). "
            "Lin's CCC = Pearson r × C_b. "
            "A high r with low C_b indicates raters agree on ranking but "
            "differ systematically in their absolute scores (scale or location bias)."
        ),
        "assumptions": [
            "Exactly 2 raters required for Lin's CCC.",
            "Scores are continuous or approximately interval-level.",
            "Each unit is rated independently.",
            "CCC ≤ Pearson r always holds — the gap reflects systematic bias.",
        ],
        "nonparam": "Krippendorff's α (interval metric)",
        "nonparam_when": (
            "Krippendorff's α handles missing data and complements ICC and CCC "
            "as a non-parametric alternative."
        ),
    },

    # ── Reliability Analysis ─────────────────────────────────
    "Reliability Analysis": {
        "csv": (
            "subject_id,MOT1,MOT2,MOT3,MOT4,ENG1,ENG2,ENG3,ENG4,ANX1,ANX2,ANX3,ANX4_R\n"
            "1,1,1,1,1,3,4,5,3,3,4,3,3\n2,3,3,3,4,4,3,5,2,4,3,3,4\n3,3,3,1,4,3,2,4,4,3,3,4,2\n4,2,3,2,2,3,1,2,3,4,4,4,1\n5,1,1,1,2,4,3,4,3,2,2,3,3\n"
            "6,4,3,3,4,3,1,1,1,3,3,4,2\n7,3,3,2,2,1,1,1,1,4,4,4,2\n8,3,3,3,3,1,3,1,3,3,2,2,2\n9,3,4,4,5,4,4,4,4,3,4,4,2\n10,3,3,2,3,5,3,3,4,2,3,3,3\n"
            "11,3,2,2,2,4,5,1,4,4,3,4,3\n12,4,4,5,3,5,3,4,3,3,3,4,2\n13,4,4,3,2,1,2,3,2,1,1,2,4\n14,2,3,3,3,3,3,2,5,2,2,2,3\n15,2,2,2,2,4,2,3,1,1,1,2,4\n"
            "16,1,2,2,3,3,2,1,3,3,3,2,4\n17,2,3,3,1,3,2,3,4,3,4,4,1\n18,4,5,5,4,3,2,2,1,3,4,3,3\n19,3,2,4,2,2,4,2,2,2,1,3,4\n20,4,5,4,5,4,2,3,3,3,2,2,3\n"
            "21,3,3,2,2,4,4,5,3,4,3,3,3\n22,3,3,2,2,3,3,3,2,2,5,3,3\n23,2,2,1,1,3,2,2,1,3,1,3,4\n24,4,2,4,3,5,3,3,2,4,4,3,3\n25,5,5,4,4,3,3,3,4,3,4,3,1\n"
            "26,2,3,3,1,2,2,2,1,3,4,4,3\n27,3,5,3,4,3,3,3,4,3,3,4,2\n28,3,3,4,3,2,3,4,3,5,5,5,2\n29,3,4,4,4,2,5,2,1,5,4,3,2\n30,3,4,3,2,1,3,4,4,4,3,4,2"
        ),
        "desc": (
            "Assess the <b>internal consistency reliability</b> of one or more "
            "constructs (item sets). Computes Cronbach\u2019s alpha, KR-20, "
            "split-half, Guttman\u2019s lambda, ICC and McDonald\u2019s omega for "
            "<b>each construct</b> in a single run."
        ),
        "note": (
            "One file, multiple constructs. Each column is an item; assign items "
            "to constructs in the sidebar. Sample has 3 constructs "
            "(MOT, ENG, ANX); ANX4_R is reverse-scored to demonstrate detection."
        ),
        "use_when": (
            "Use reliability analysis to evaluate whether a set of items "
            "consistently measures the same underlying construct, prior to "
            "computing scale scores. Cronbach\u2019s alpha is the standard index; "
            "KR-20 applies to dichotomous items; McDonald\u2019s omega is "
            "recommended when items are not strictly tau-equivalent."
        ),
        "assumptions": [
            "Items are scored in the same direction (reverse items recoded).",
            "Items measure a single underlying construct (unidimensional).",
            "Observations are independent (one row per respondent).",
            "Interval-level measurement is assumed for alpha (ordinal often "
            "acceptable in practice).",
        ],
        "nonparam": "KR-20 (dichotomous) / Guttman\u2019s lambda / McDonald\u2019s omega",
        "nonparam_when": (
            "KR-20 is reported automatically for dichotomous (0/1) items; "
            "omega and Guttman\u2019s lambda are always reported alongside alpha."
        ),
    },

}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_test_names():
    """Return list of all available test names."""
    return list(SAMPLES.keys())


def get_sample_df(test_name):
    """
    Return a pandas DataFrame for the built-in sample data of a given test.

    Parameters
    ----------
    test_name : str
        Must be a key in SAMPLES.

    Returns
    -------
    pd.DataFrame
    """
    import pandas as pd
    import io
    if test_name not in SAMPLES:
        raise KeyError(f"No sample data found for test: '{test_name}'")
    return pd.read_csv(io.StringIO(SAMPLES[test_name]["csv"]))


def get_test_info(test_name):
    """
    Return the full metadata dict for a given test.

    Parameters
    ----------
    test_name : str

    Returns
    -------
    dict with keys: desc, note, use_when, assumptions, nonparam, nonparam_when
    """
    if test_name not in SAMPLES:
        raise KeyError(f"No info found for test: '{test_name}'")
    return SAMPLES[test_name]


# ══════════════════════════════════════════════════════════════════════════════
# TEST CATEGORIES (for homepage card grouping)
# ══════════════════════════════════════════════════════════════════════════════

TEST_CATEGORIES = {
    "T-Tests": [
        "One-Sample T-Test",
        "Paired-Sample T-Test",
        "Independent-Sample T-Test",
    ],
    "ANOVA": [
        "One-Way ANOVA",
        "Factorial ANOVA",
        "Repeated Measures ANOVA",
        "Mixed ANOVA",
    ],
    "ANCOVA": [
        "One-Way ANCOVA",
        "Factorial ANCOVA",
        "Repeated Measures ANCOVA",
        "Mixed ANCOVA",
        "MANCOVA",
    ],
    "Regression": [
        "Linear Regression",
        "Multiple Regression",
    ],
    "Correlation": [
        "Bivariate Correlation",
    ],
    "Reliability": [
        "Reliability Analysis",
    ],
    "Inter-Rater Agreement": [
        "IRAR Dichotomous",
        "IRAR Nominal",
        "IRAR Ordinal",
        "IRAR Ordinal Multi",
        "IRAR Interval",
        "IRAR Interval 2-rater",
    ],
}


def get_category(test_name):
    """Return the category name for a given test."""
    for cat, tests in TEST_CATEGORIES.items():
        if test_name in tests:
            return cat
    return "Other"
