"""
content/test_guide.py
=====================
Homepage card content and test selection guidance for all statistical tests.

Each entry contains structured academic-English descriptions used to render
the homepage selection cards. Users read these cards to understand which
test is appropriate for their research design before proceeding.

The content covers:
  - When to use the test (use_when)
  - What the test does (desc)
  - Key statistical assumptions (assumptions)
  - Non-parametric equivalent and when to switch (nonparam, nonparam_when)
  - Data format requirements (data_format)
  - Example research questions (example)
  - References (references)

Design principle:
  Cards are grouped by category (T-Tests, ANOVA, ANCOVA, Regression).
  Each card shows: title, short desc, "Use when" summary, and non-param alt.
  Clicking a card navigates to the corresponding analysis page.
"""


# ══════════════════════════════════════════════════════════════════════════════
# TEST GUIDE CONTENT
# ══════════════════════════════════════════════════════════════════════════════

TEST_GUIDE = {

    # ── T-TESTS ────────────────────────────────────────────────────────────────

    "One-Sample T-Test": {
        "icon":     "🎯",
        "category": "T-Tests",
        "short":    "Compare one group mean to a known value.",
        "desc": (
            "Test whether the mean of a single continuous variable "
            "differs significantly from a pre-specified hypothesised "
            "population mean (\u03bc\u2080)."
        ),
        "use_when": (
            "Use when you have one continuous dependent variable measured on "
            "a single group and wish to determine whether the sample mean "
            "deviates significantly from a known reference value "
            "(e.g., a national norm, a theoretical threshold, or a "
            "population mean reported in prior literature)."
        ),
        "use_when_short": (
            "One group \u2014 testing whether its mean equals a known value (\u03bc\u2080)"
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Observations are independent of one another.",
            "The dependent variable is approximately normally distributed "
            "(Shapiro-Wilk for Total N < 50; "
            "Kolmogorov-Smirnov with Lilliefors correction for Total N \u2265 50).",
        ],
        "data_format": (
            "One numeric column. "
            "Set the hypothesised population mean (\u03bc\u2080) before running."
        ),
        "example": (
            "Is the average exam score of a class of 30 students "
            "significantly different from the national average of 75?"
        ),
        "nonparam":       "Wilcoxon Signed-Rank Test",
        "nonparam_when":  "Normality assumption violated (primary criterion p \u2264 .05).",
        "effect_size":    "Cohen\u2019s d; Rank-biserial r (non-parametric)",
        "spss_equivalent": "Analyze \u2192 Compare Means \u2192 One-Sample T Test",
        "references": [
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    "Paired-Sample T-Test": {
        "icon":     "🔁",
        "category": "T-Tests",
        "short":    "Compare two related measurements from the same participants.",
        "desc": (
            "Test whether the mean difference between two related variables "
            "(e.g., pre-test and post-test scores from the same participants) "
            "is significantly different from zero."
        ),
        "use_when": (
            "Use when the same participants are measured under two conditions "
            "or at two time points, and you wish to determine whether the "
            "mean change is statistically significant. "
            "Also known as the Dependent Samples T-Test or Repeated "
            "Measures T-Test."
        ),
        "use_when_short": (
            "Same participants, two measurements \u2014 "
            "testing whether the mean change equals zero"
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "Observations are paired \u2014 each score in Variable 1 "
            "corresponds to a score in Variable 2 from the same subject.",
            "The differences (Variable 1 \u2212 Variable 2) are approximately "
            "normally distributed "
            "(Shapiro-Wilk for Total N < 50; "
            "Kolmogorov-Smirnov with Lilliefors correction for Total N \u2265 50).",
        ],
        "data_format": (
            "Two numeric columns: Variable 1 (pre / Time 1) and "
            "Variable 2 (post / Time 2). Both from the same subjects."
        ),
        "example": (
            "Did students\u2019 anxiety scores decrease significantly "
            "after an eight-week mindfulness intervention?"
        ),
        "nonparam":       "Wilcoxon Signed-Rank Test",
        "nonparam_when":  "Normality of differences violated (primary criterion p \u2264 .05).",
        "effect_size":    "Cohen\u2019s d; Rank-biserial r (non-parametric)",
        "spss_equivalent": "Analyze \u2192 Compare Means \u2192 Paired-Samples T Test",
        "references": [
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    "Independent-Sample T-Test": {
        "icon":     "⚖️",
        "category": "T-Tests",
        "short":    "Compare means from two independent groups.",
        "desc": (
            "Test whether the means of a continuous dependent variable "
            "differ significantly between two independent groups."
        ),
        "use_when": (
            "Use when you have two separate, unrelated groups "
            "(e.g., control vs. treatment, male vs. female) and wish to "
            "determine whether their population means on a continuous "
            "outcome variable are significantly different. "
            "Levene\u2019s test determines whether to apply the standard "
            "equal-variance t-test or the Welch correction."
        ),
        "use_when_short": (
            "Two independent groups \u2014 testing whether their means differ"
        ),
        "assumptions": [
            "The dependent variable is continuous (interval or ratio scale).",
            "The two groups are independent \u2014 participants belong to one group only.",
            "The dependent variable is approximately normally distributed "
            "within each group, assessed based on Total N: "
            "Shapiro-Wilk for Total N < 50; "
            "Kolmogorov-Smirnov with Lilliefors correction for Total N \u2265 50.",
            "Homogeneity of variance across groups "
            "(Levene\u2019s test, center = mean). "
            "If violated, the Welch correction is applied automatically.",
        ],
        "data_format": (
            "One categorical grouping column and one numeric outcome column. "
            "The grouping column must contain exactly two distinct group labels."
        ),
        "example": (
            "Do students taught with a new pedagogical method score "
            "significantly higher on the final exam than those taught "
            "with the traditional method?"
        ),
        "nonparam":       "Mann-Whitney U Test",
        "nonparam_when":  "Normality violated in one or both groups (primary criterion p \u2264 .05).",
        "effect_size":    "Cohen\u2019s d; Rank-biserial r (non-parametric)",
        "spss_equivalent": "Analyze \u2192 Compare Means \u2192 Independent-Samples T Test",
        "references": [
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Welch, B. L. (1947). The generalization of Student\u2019s problem.",
        ],
    },

    # ── ANOVA ──────────────────────────────────────────────────────────────────

    "One-Way ANOVA": {
        "icon":     "📊",
        "category": "ANOVA",
        "short":    "Compare means across three or more independent groups.",
        "desc": (
            "Test whether the means of a continuous dependent variable "
            "differ significantly across three or more independent groups."
        ),
        "use_when": (
            "Use when you have one continuous dependent variable and one "
            "categorical independent variable (factor) with three or more "
            "levels, and wish to test for overall mean differences. "
            "If significant, follow up with post-hoc tests "
            "(e.g., Tukey HSD, Bonferroni) to identify which pairs differ."
        ),
        "use_when_short": (
            "Three or more independent groups \u2014 testing overall mean differences"
        ),
        "assumptions": [
            "The dependent variable is continuous.",
            "Groups are independent of one another.",
            "Approximate normality within each group.",
            "Homogeneity of variance across groups (Levene\u2019s test).",
        ],
        "data_format": (
            "One categorical grouping column (3+ levels) and "
            "one numeric outcome column."
        ),
        "example": (
            "Do students in three different teaching conditions "
            "(lecture, flipped classroom, and hybrid) differ significantly "
            "in their final exam scores?"
        ),
        "nonparam":       "Kruskal-Wallis Test",
        "nonparam_when":  "Normality or homogeneity of variance assumptions violated.",
        "effect_size":    "\u03b7\u00b2 (eta-squared); \u03c9\u00b2 (omega-squared, less biased)",
        "spss_equivalent": "Analyze \u2192 Compare Means \u2192 One-Way ANOVA",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
        ],
    },

    "Factorial ANOVA": {
        "icon":     "🔢",
        "category": "ANOVA",
        "short":    "Examine main effects and interactions of two or more factors.",
        "desc": (
            "Test the main effects of two or more categorical factors "
            "and their interaction effect on a continuous dependent variable."
        ),
        "use_when": (
            "Use when you have two or more categorical independent variables "
            "(factors) and wish to examine their individual main effects and "
            "their combined interaction effect on a continuous outcome. "
            "The interaction term reveals whether the effect of one factor "
            "depends on the level of another."
        ),
        "use_when_short": (
            "Two or more factors \u2014 testing main effects and interactions"
        ),
        "assumptions": [
            "The dependent variable is continuous.",
            "Groups are independent of one another.",
            "Approximate normality within each cell (combination of factor levels).",
            "Homogeneity of variance across all cells (Levene\u2019s test).",
        ],
        "data_format": (
            "Two categorical factor columns and one numeric outcome column. "
            "Each factor must have two or more levels."
        ),
        "example": (
            "Do teaching method and student gender interact to affect "
            "academic achievement?"
        ),
        "nonparam":       "Scheirer-Ray-Hare Test",
        "nonparam_when":  "Normality or homogeneity assumptions violated.",
        "effect_size":    "Partial \u03b7\u00b2 (partial eta-squared)",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Univariate",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    "Repeated Measures ANOVA": {
        "icon":     "🔄",
        "category": "ANOVA",
        "short":    "Test changes across three or more time points in the same participants.",
        "desc": (
            "Test whether a continuous dependent variable changes "
            "significantly across three or more time points or conditions "
            "measured on the same participants."
        ),
        "use_when": (
            "Use when the same participants are measured on the same continuous "
            "outcome variable at three or more time points or under three or "
            "more conditions. Controls for individual differences and is more "
            "statistically powerful than between-subjects designs."
        ),
        "use_when_short": (
            "Same participants, three or more measurements \u2014 "
            "testing change over time"
        ),
        "assumptions": [
            "The dependent variable is continuous.",
            "Observations are from the same subjects across all time points.",
            "Approximate normality at each time point.",
            "Sphericity: equal variances of differences between all pairs of "
            "time points (Mauchly\u2019s test). "
            "If violated, Greenhouse-Geisser or Huynh-Feldt correction applied.",
        ],
        "data_format": (
            "Wide-format data: one column per time point, one row per subject. "
            "All measurement columns must be numeric."
        ),
        "example": (
            "Did students\u2019 motivation scores change significantly "
            "across three semesters?"
        ),
        "nonparam":       "Friedman Test",
        "nonparam_when":  "Normality or sphericity assumptions substantially violated.",
        "effect_size":    "Partial \u03b7\u00b2; \u03c9\u00b2",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Repeated Measures",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Greenhouse, S. W., & Geisser, S. (1959). Psychometrika, 24(2), 95\u2013112.",
        ],
    },

    "Mixed ANOVA": {
        "icon":     "🔀",
        "category": "ANOVA",
        "short":    "Test between-subjects and within-subjects effects simultaneously.",
        "desc": (
            "Test the effects of a between-subjects factor (group), "
            "a within-subjects factor (time), and their interaction "
            "on a continuous dependent variable."
        ),
        "use_when": (
            "Use when your design includes both a between-subjects factor "
            "(e.g., treatment vs. control group) and a within-subjects factor "
            "(e.g., measurements at multiple time points). "
            "The critical result is typically the interaction effect, which "
            "indicates whether the trajectory of change over time differs "
            "between groups."
        ),
        "use_when_short": (
            "Between-subjects factor (group) + within-subjects factor (time) "
            "\u2014 testing their interaction"
        ),
        "assumptions": [
            "The dependent variable is continuous.",
            "Between-subjects groups are independent.",
            "Within-subjects measurements come from the same participants.",
            "Approximate normality within each cell.",
            "Homogeneity of variance across between-subjects groups.",
            "Sphericity of the within-subjects factor (Mauchly\u2019s test).",
        ],
        "data_format": (
            "One categorical grouping column (between-subjects factor) and "
            "multiple numeric columns (one per time point / within-subjects condition)."
        ),
        "example": (
            "Does the effectiveness of a training programme "
            "(measured at baseline, midpoint, and follow-up) differ "
            "between experimental and control groups?"
        ),
        "nonparam":       "Aligned Ranks Transform (ART) ANOVA",
        "nonparam_when":  "Normality assumptions substantially violated.",
        "effect_size":    "Partial \u03b7\u00b2 for each effect",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Repeated Measures",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    # ── ANCOVA ─────────────────────────────────────────────────────────────────

    "One-Way ANCOVA": {
        "icon":     "🎛️",
        "category": "ANCOVA",
        "short":    "Compare group means while controlling for a covariate.",
        "desc": (
            "Test group mean differences on a continuous dependent variable "
            "while statistically controlling for one or more continuous "
            "covariates."
        ),
        "use_when": (
            "Use when you wish to compare group means on a continuous outcome "
            "while removing the influence of one or more continuous covariates "
            "(confounding variables). ANCOVA reduces error variance and "
            "increases statistical power by accounting for pre-existing "
            "differences between groups."
        ),
        "use_when_short": (
            "Two or more groups \u2014 comparing means after adjusting for a covariate"
        ),
        "assumptions": [
            "The dependent variable and covariate are continuous.",
            "Groups are independent.",
            "Linear relationship between covariate and outcome within each group.",
            "Homogeneity of regression slopes "
            "(group \u00d7 covariate interaction not significant).",
            "Approximate normality of residuals within each group.",
            "Homogeneity of variance (Levene\u2019s test).",
        ],
        "data_format": (
            "One categorical grouping column, one numeric covariate column, "
            "and one numeric outcome column."
        ),
        "example": (
            "After controlling for pre-test scores, do students in the "
            "experimental group score significantly higher on the post-test "
            "than those in the control group?"
        ),
        "nonparam":       "Quade Test / Rank ANCOVA",
        "nonparam_when":  "Normality assumptions violated.",
        "effect_size":    "Partial \u03b7\u00b2",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Univariate (with covariate)",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Miller, G. A., & Chapman, J. P. (2001). Psychological Methods, 6(2), 203.",
        ],
    },

    "Factorial ANCOVA": {
        "icon":     "🎚️",
        "category": "ANCOVA",
        "short":    "Test factorial effects while controlling for covariates.",
        "desc": (
            "Test the main effects of two or more factors and their interaction "
            "on a continuous dependent variable while controlling for covariates."
        ),
        "use_when": (
            "Use when you have a factorial design (multiple categorical factors) "
            "and wish to control for the influence of one or more continuous "
            "covariates. Combines the logic of Factorial ANOVA and ANCOVA."
        ),
        "use_when_short": (
            "Two or more factors + covariate(s) \u2014 testing main effects and interactions"
        ),
        "assumptions": [
            "The dependent variable and covariate(s) are continuous.",
            "Groups are independent.",
            "Linear covariate-outcome relationship.",
            "Homogeneity of regression slopes across all cells.",
            "Normality of residuals within each cell.",
            "Homogeneity of variance.",
        ],
        "data_format": (
            "Two categorical factor columns, one or more numeric covariate columns, "
            "and one numeric outcome column."
        ),
        "example": (
            "After controlling for prior achievement, do teaching method "
            "and socioeconomic status interact to affect learning outcomes?"
        ),
        "nonparam":       "Rank-based ANCOVA",
        "nonparam_when":  "Normality assumptions violated.",
        "effect_size":    "Partial \u03b7\u00b2 for each effect",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Univariate",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    # ── Repeated Measures ANCOVA ───────────────────────────────────────────────

    "Repeated Measures ANCOVA": {
        "icon":     "\u23f1\ufe0f",
        "category": "ANCOVA",
        "short":    "Compare repeated measurements while controlling for a covariate.",
        "desc": (
            "Test within-subjects time effects on a continuous dependent variable "
            "across multiple time points while statistically controlling for a "
            "continuous between-subjects covariate."
        ),
        "use_when": (
            "Use Repeated Measures ANCOVA when the same participants are measured "
            "at two or more time points and you wish to control for a covariate "
            "(e.g., age, baseline score) that may vary between participants. "
            "This increases precision and removes confounding variance."
        ),
        "use_when_short": (
            "Same participants measured repeatedly \u2014 controlling for a between-subjects covariate"
        ),
        "assumptions": [
            "The dependent variable is continuous and measured at each time point.",
            "The covariate is continuous and measured once per subject.",
            "Sphericity of the within-subjects factor (Mauchly\u2019s test; GG correction applied).",
            "Linearity between covariate and dependent variable.",
            "Homogeneity of regression slopes across time points.",
            "Normality of residuals at each time point.",
        ],
        "data_format": (
            "One numeric covariate column (per subject) and one column per time point."
        ),
        "example": (
            "After controlling for participants\u2019 age, do anxiety scores "
            "change significantly across pre-test, mid-test, and post-test?"
        ),
        "nonparam":       "Friedman Test (without covariate adjustment)",
        "nonparam_when":  "Normality assumptions severely violated.",
        "effect_size":    "Partial \u03b7\u00b2",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Repeated Measures (with covariate)",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Tabachnick, B. G., & Fidell, L. S. (2013). Using multivariate statistics (6th ed.).",
        ],
    },

    # ── Mixed ANCOVA ───────────────────────────────────────────────────────────

    "Mixed ANCOVA": {
        "icon":     "\u2697\ufe0f",
        "category": "ANCOVA",
        "short":    "Between \u00d7 within design with covariate control.",
        "desc": (
            "Test between-subjects, within-subjects, and interaction effects on "
            "a continuous dependent variable while controlling for a covariate. "
            "Combines Mixed ANOVA with covariate adjustment."
        ),
        "use_when": (
            "Use Mixed ANCOVA when you have both a between-subjects factor "
            "(e.g., treatment vs. control group) and a within-subjects factor "
            "(e.g., time points), and you wish to control for a continuous "
            "covariate (e.g., baseline score, age)."
        ),
        "use_when_short": (
            "Between \u00d7 within design \u2014 group differences over time, controlling for a covariate"
        ),
        "assumptions": [
            "Between-subjects factor is categorical; time points are continuous.",
            "The covariate is linearly related to the dependent variable.",
            "Homogeneity of regression slopes across groups and time.",
            "Normality of residuals within each cell.",
            "Homogeneity of variance across between-subjects groups (Levene\u2019s test).",
            "Sphericity for within-subjects effects (GG correction applied).",
        ],
        "data_format": (
            "One between-subjects factor column, one numeric covariate column, "
            "and one column per time point."
        ),
        "example": (
            "After controlling for baseline anxiety, does the treatment group "
            "show greater improvement in anxiety scores over three time points "
            "compared to the control group?"
        ),
        "nonparam":       "Aligned Rank Transform ANOVA (ART-ANOVA)",
        "nonparam_when":  "Normality assumptions violated.",
        "effect_size":    "Partial \u03b7\u00b2 for each effect",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Repeated Measures (with between factor + covariate)",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    # ── MANCOVA ────────────────────────────────────────────────────────────────

    "MANCOVA": {
        "icon":     "📊",
        "category": "ANCOVA",
        "short":    "Multiple DVs simultaneously, controlling for a covariate.",
        "desc": (
            "Test group differences on two or more continuous dependent variables "
            "simultaneously while controlling for a covariate. "
            "Uses multivariate test statistics to protect against inflated Type I error."
        ),
        "use_when": (
            "Use MANCOVA when you have multiple correlated dependent variables "
            "and wish to compare groups while controlling for a covariate. "
            "It is more powerful and statistically appropriate than running "
            "separate ANCOVAs when DVs are related."
        ),
        "use_when_short": (
            "Multiple dependent variables \u2014 group comparison with covariate adjustment"
        ),
        "assumptions": [
            "All dependent variables and the covariate are continuous.",
            "Groups are independent of one another.",
            "Multivariate normality of residuals.",
            "Homogeneity of variance-covariance matrices (Box\u2019s M test).",
            "No excessive multicollinearity among dependent variables.",
            "Linear relationships between the covariate and each DV.",
            "Homogeneity of regression slopes across groups.",
        ],
        "data_format": (
            "One categorical factor column, one numeric covariate column, "
            "and two or more numeric dependent variable columns."
        ),
        "example": (
            "After controlling for IQ, do three teaching methods (A, B, C) "
            "differ significantly on both reading and mathematics scores?"
        ),
        "nonparam":       "Rank-based MANCOVA",
        "nonparam_when":  "Multivariate normality severely violated.",
        "effect_size":    "Wilks\u2019 \u039b, Pillai\u2019s Trace, Partial \u03b7\u00b2 per DV",
        "spss_equivalent": "Analyze \u2192 General Linear Model \u2192 Multivariate (with covariate)",
        "references": [
            "Tabachnick, B. G., & Fidell, L. S. (2013). Using multivariate statistics (6th ed.).",
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    # ── REGRESSION ─────────────────────────────────────────────────────────────

    "Linear Regression": {
        "icon":     "📈",
        "category": "Regression",
        "short":    "Model the linear relationship between one predictor and one outcome.",
        "desc": (
            "Examine the linear relationship between one continuous predictor "
            "and one continuous outcome variable, and quantify how much of the "
            "variance in the outcome is explained by the predictor."
        ),
        "use_when": (
            "Use when you wish to model the linear relationship between one "
            "continuous predictor (independent variable) and one continuous "
            "outcome (dependent variable), and to predict outcome values "
            "from predictor values."
        ),
        "use_when_short": (
            "One predictor, one continuous outcome \u2014 modelling their linear relationship"
        ),
        "assumptions": [
            "Both variables are continuous (interval or ratio scale).",
            "Linear relationship between predictor and outcome.",
            "Residuals are approximately normally distributed.",
            "Homoscedasticity: residuals have constant variance across fitted values.",
            "Observations are independent.",
            "No influential outliers (Cook\u2019s Distance).",
        ],
        "data_format": (
            "One numeric predictor column and one numeric outcome column."
        ),
        "example": (
            "Does study time significantly predict exam performance?"
        ),
        "nonparam":       "Spearman Rank Correlation / Theil-Sen Estimator",
        "nonparam_when":  "Normality or linearity assumptions violated.",
        "effect_size":    "R\u00b2 (coefficient of determination)",
        "spss_equivalent": "Analyze \u2192 Regression \u2192 Linear",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
        ],
    },

    "Multiple Regression": {
        "icon":     "📉",
        "category": "Regression",
        "short":    "Model the simultaneous effects of multiple predictors on one outcome.",
        "desc": (
            "Examine the simultaneous linear effects of two or more predictors "
            "on a continuous outcome variable, and assess the unique "
            "contribution of each predictor."
        ),
        "use_when": (
            "Use when you wish to predict a continuous outcome from two or more "
            "predictors simultaneously, to control for confounders, or to assess "
            "the relative importance of each predictor while holding others "
            "constant."
        ),
        "use_when_short": (
            "Multiple predictors, one continuous outcome \u2014 "
            "assessing unique contributions of each predictor"
        ),
        "assumptions": [
            "The outcome variable is continuous.",
            "All predictors are continuous or dichotomous (dummy-coded).",
            "Linear relationships between each predictor and the outcome.",
            "Residuals are approximately normally distributed.",
            "Homoscedasticity of residuals.",
            "No multicollinearity (VIF < 10).",
            "Observations are independent.",
            "No influential outliers (Cook\u2019s Distance).",
        ],
        "data_format": (
            "Two or more numeric predictor columns and one numeric outcome column. "
            "Dichotomous variables (0/1) may be included as predictors."
        ),
        "example": (
            "Do study time, motivation, and prior GPA jointly and independently "
            "predict final exam performance?"
        ),
        "nonparam":       "Robust Regression / Quantile Regression",
        "nonparam_when":  "Normality or homoscedasticity assumptions substantially violated.",
        "effect_size":    "R\u00b2; Adjusted R\u00b2; \u0394R\u00b2 (change in R\u00b2)",
        "spss_equivalent": "Analyze \u2192 Regression \u2192 Linear",
        "references": [
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
        ],
    },

    "Bivariate Correlation": {
        "icon":     "🔗",
        "category": "Correlation",
        "short":    "Measure the strength and direction of association between variables.",
        "desc": (
            "Quantify the strength and direction of the relationship between "
            "two or more continuous variables, without designating predictors "
            "or outcomes. The appropriate coefficient is selected automatically."
        ),
        "use_when": (
            "Use bivariate correlation when you wish to measure how strongly "
            "two continuous variables are associated, and in which direction, "
            "without modelling one as a predictor of the other."
        ),
        "use_when_short": (
            "Two or more variables \u2014 measuring how strongly they are associated"
        ),
        "assumptions": [
            "Variables are continuous (interval/ratio) or ordinal.",
            "Observations are independent (one row per case).",
            "Pearson: both variables normally distributed and linearly related.",
            "Spearman / Kendall: the relationship is monotonic.",
        ],
        "data_format": (
            "Two or more numeric columns. Each pair of variables is correlated."
        ),
        "example": (
            "How strongly are study hours, motivation, and exam scores related?"
        ),
        "nonparam":       "Spearman\u2019s rho / Kendall\u2019s tau-b",
        "nonparam_when":  "Normality or linearity violated (selected automatically).",
        "effect_size":    "r / \u03c1 / \u03c4 (correlation coefficient is itself the effect size); r\u00b2 shared variance",
        "spss_equivalent": "Analyze \u2192 Correlate \u2192 Bivariate",
        "references": [
            "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.).",
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

    "Reliability Analysis": {
        "icon":     "🧪",
        "category": "Reliability",
        "short":    "Assess internal consistency reliability of one or more constructs.",
        "desc": (
            "Evaluate how consistently a set of items measures an underlying "
            "construct. Computes Cronbach\u2019s alpha, KR-20, split-half, "
            "Guttman\u2019s lambda, ICC and McDonald\u2019s omega \u2014 for multiple "
            "constructs from a single file in one run."
        ),
        "use_when": (
            "Use reliability analysis before computing scale scores, to verify "
            "that items intended to measure the same construct hang together."
        ),
        "use_when_short": (
            "Item sets (scales) \u2014 checking internal consistency reliability"
        ),
        "assumptions": [
            "Items scored in the same direction (reverse items recoded).",
            "Items measure a single underlying construct (unidimensional).",
            "Observations are independent (one row per respondent).",
            "Interval-level measurement assumed for alpha.",
        ],
        "data_format": (
            "One file; each column is an item. Assign items to constructs."
        ),
        "example": (
            "Is the 20-item motivation scale internally consistent (\u03b1 \u2265 .80)?"
        ),
        "nonparam":       "KR-20 / Guttman\u2019s \u03bb / McDonald\u2019s \u03c9",
        "nonparam_when":  "KR-20 auto-applied to dichotomous items; \u03c9 and \u03bb always reported.",
        "effect_size":    "\u03b1, \u03c9, \u03bb, ICC (reliability coefficients, range 0\u20131)",
        "spss_equivalent": "Analyze \u2192 Scale \u2192 Reliability Analysis",
        "references": [
            "Cronbach, L. J. (1951). Coefficient alpha and the internal structure of tests. Psychometrika, 16, 297\u2013334.",
            "McDonald, R. P. (1999). Test theory: A unified treatment.",
            "Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.).",
        ],
    },

}


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════

CATEGORIES = {
    "T-Tests": {
        "icon":  "📐",
        "desc":  (
            "Compare means between one group and a reference value, "
            "or between two related or independent groups. "
            "Non-parametric equivalents are applied automatically "
            "when normality assumptions are violated."
        ),
        "tests": [
            "One-Sample T-Test",
            "Paired-Sample T-Test",
            "Independent-Sample T-Test",
        ],
    },
    "ANOVA": {
        "icon":  "📊",
        "desc":  (
            "Extend mean comparisons to three or more groups, "
            "multiple factors, or repeated measurements. "
            "Non-parametric equivalents (Kruskal-Wallis, Friedman) "
            "are available when assumptions are violated."
        ),
        "tests": [
            "One-Way ANOVA",
            "Factorial ANOVA",
            "Repeated Measures ANOVA",
            "Mixed ANOVA",
        ],
    },
    "ANCOVA": {
        "icon":  "🎛️",
        "desc":  (
            "Compare group means while statistically controlling for "
            "continuous covariates. Increases precision and removes "
            "the influence of confounding variables."
        ),
        "tests": [
            "One-Way ANCOVA",
            "Factorial ANCOVA",
            "Repeated Measures ANCOVA",
            "Mixed ANCOVA",
            "MANCOVA",
        ],
    },
    "Regression": {
        "icon":  "📈",
        "desc":  (
            "Model the relationship between one or more predictors "
            "and a continuous outcome variable. "
            "Quantify the unique contribution of each predictor "
            "and predict outcome values."
        ),
        "tests": [
            "Linear Regression",
            "Multiple Regression",
        ],
    },
    "Correlation": {
        "icon":  "🔗",
        "desc":  (
            "Measure the strength and direction of association between "
            "continuous variables. Pearson, Spearman, and Kendall\u2019s tau-b "
            "are computed automatically, with the appropriate coefficient "
            "recommended based on normality and linearity."
        ),
        "tests": [
            "Bivariate Correlation",
        ],
    },
    "Reliability": {
        "icon":  "🧪",
        "desc":  (
            "Assess internal consistency reliability of measurement scales. "
            "Cronbach\u2019s alpha, KR-20, split-half, Guttman\u2019s lambda, ICC "
            "and McDonald\u2019s omega \u2014 computed for multiple constructs at once."
        ),
        "tests": [
            "Reliability Analysis",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_all_tests():
    """Return a list of all test names in display order."""
    order = []
    for cat_info in CATEGORIES.values():
        order.extend(cat_info["tests"])
    return order


def get_test_info(test_name):
    """
    Return the full guide dict for a given test.

    Parameters
    ----------
    test_name : str

    Returns
    -------
    dict or None
    """
    return TEST_GUIDE.get(test_name)


def get_category_tests(category):
    """
    Return the list of test names for a given category.

    Parameters
    ----------
    category : str — e.g. 'T-Tests', 'ANOVA'

    Returns
    -------
    list of str
    """
    return CATEGORIES.get(category, {}).get("tests", [])


def get_test_category(test_name):
    """Return the category name for a given test."""
    for cat, info in CATEGORIES.items():
        if test_name in info["tests"]:
            return cat
    return "Other"


def get_card_content(test_name):
    """
    Return condensed card content for homepage display.

    Parameters
    ----------
    test_name : str

    Returns
    -------
    dict with keys: icon, short, use_when_short, nonparam, category
    """
    info = TEST_GUIDE.get(test_name, {})
    return {
        "icon":           info.get("icon", "\U0001f4ca"),
        "short":          info.get("short", ""),
        "use_when_short": info.get("use_when_short", ""),
        "nonparam":       info.get("nonparam", ""),
        "category":       info.get("category", ""),
        "effect_size":    info.get("effect_size", ""),
    }


def get_assumptions(test_name):
    """
    Return the list of statistical assumptions for a given test.

    Parameters
    ----------
    test_name : str

    Returns
    -------
    list of str
    """
    return TEST_GUIDE.get(test_name, {}).get("assumptions", [])


def get_spss_path(test_name):
    """
    Return the SPSS menu path equivalent for a given test.

    Parameters
    ----------
    test_name : str

    Returns
    -------
    str
    """
    return TEST_GUIDE.get(test_name, {}).get("spss_equivalent", "")
