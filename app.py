"""
app.py
======
Homepage for Inferential Statistics by Muhaimin Abdullah

Displays categorised test selection cards. Each card shows:
  - Test name and icon
  - One-sentence description
  - "Use when" summary
  - Non-parametric equivalent
  - Effect size measures

Users click a card to navigate to the corresponding analysis page.
Currently active: T-Tests (pages/1_T_Tests.py)
Coming soon: ANOVA, ANCOVA, Regression
"""

import streamlit as st
from content.test_guide import TEST_GUIDE, CATEGORIES, get_card_content

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResMeth: Inferential Statistics Calculator",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
section[data-testid="stSidebar"] { display: none !important; }

.hero {
    background: linear-gradient(120deg, #0a0a0a 0%, #1a1a2e 40%, #16213e 100%);
    padding: 2.8rem 3rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    border-left: 6px solid #e94560;
    box-shadow: 0 12px 40px rgba(233, 69, 96, .18);
}
.hero h1 {
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 .25rem 0;
    letter-spacing: -.5px;
}
.hero h2 {
    color: #fff;
    font-size: 1.5rem;
    font-weight: 500;
    margin: 0 0 0 0;
}
.hero h3 {
    color: #fff;
    font-size: 1.25rem;
    font-weight: 500;
    margin: 0 0 .25rem 0;
}
.hero p {
    color: #94a3b8;
    font-size: .95rem;
    margin: 0 0 1.4rem;
    line-height: 1.7;
}
.hero-badges { margin-bottom: 1.6rem; }
.badge {
    display: inline-block;
    background: #e94560;
    color: #fff;
    font-size: .7rem;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 4px;
}
.badge.outline {
    background: transparent;
    border: 1px solid rgba(255,255,255,.25);
    color: #94a3b8;
}
.qris-wrap {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,.1);
    display: flex;
    align-items: center;
    gap: 16px;
}
.qris-wrap p {
    color: #64748b;
    font-size: .76rem;
    margin: 0 0 8px;
}

.cat-hdr {
    font-size: .78rem;
    font-weight: 700;
    color: #e94560;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 2rem 0 .8rem;
    padding-bottom: .4rem;
    border-bottom: 2px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 8px;
}
.cat-desc {
    font-size: .82rem;
    color: #64748b;
    margin-bottom: 1rem;
    line-height: 1.6;
}

.test-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    height: 100%;
    box-shadow: 0 2px 10px rgba(0,0,0,.05);
    transition: box-shadow .2s, transform .2s;
    position: relative;
    overflow: hidden;
}
.test-card:hover {
    box-shadow: 0 8px 28px rgba(233,69,96,.12);
    transform: translateY(-2px);
}
.test-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: #e94560;
}
.test-card.coming-soon {
    opacity: .6;
    pointer-events: none;
}
.test-card.coming-soon::before {
    background: #94a3b8;
}
.card-icon {
    font-size: 1.6rem;
    margin-bottom: .6rem;
    display: block;
}
.card-title {
    font-size: .95rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0 0 .4rem;
}
.card-short {
    font-size: .82rem;
    color: #475569;
    margin: 0 0 .8rem;
    line-height: 1.5;
}
.card-use {
    font-size: .76rem;
    color: #64748b;
    margin: 0 0 .8rem;
    line-height: 1.6;
    border-left: 2px solid #e94560;
    padding-left: 8px;
}
.card-np {
    display: inline-block;
    background: #f1f5f9;
    color: #64748b;
    font-size: .68rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    margin-right: 4px;
    margin-bottom: 4px;
}
.card-es {
    display: inline-block;
    background: #fef3c7;
    color: #92400e;
    font-size: .68rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
}
.coming-tag {
    display: inline-block;
    background: #f1f5f9;
    color: #94a3b8;
    font-size: .68rem;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    margin-top: .6rem;
}

.spss-note {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border-left: 4px solid #0284c7;
    padding: 1rem 1.2rem;
    border-radius: 0 10px 10px 0;
    font-size: .84rem;
    color: #0c4a6e;
    margin: 1.5rem 0;
    line-height: 1.7;
}
.method-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: .8rem;
    margin: 1rem 0;
}
.method-item {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: .8rem 1rem;
    font-size: .8rem;
    color: #1e293b;
}
.method-item b { color: #e94560; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>&#128208; ResMeth: Inferential Statistics Calculator</h1>
  <h2>by Muhaimin Abdullah | fully funded by <b>BIMA KEMDIKTISAINTEK</b></h2>
  <h3>Contract No. 0419/C3/DT.05.00/2025 | Deriv: 090/C3/DT.05.00/PL/2025 | Supported by LPPM Unesa</h3>
  <p>
    A comprehensive, SPSS-equivalent statistical analysis suite for
    researchers, academics, and students. Select a test below to begin.
    Parametric and non-parametric analyses are applied automatically
    based on your data.
  </p>
  <div class="hero-badges">
    <span class="badge">SPSS-Equivalent Output</span>
    <span class="badge">Auto Parametric/Non-Parametric</span>
    <span class="badge">APA 7th Edition Write-Up</span>
    <span class="badge">HTML &amp; CSV Export</span>
    <span class="badge outline">Cohen&#39;s d &middot; Rank-biserial r &middot; Power Analysis</span>
  </div>
  <div class="qris-wrap">
    <div>
      <p>&#9749; Support this work &mdash; scan QRIS <a href="https://paypal.me/mhmnbdllh" target="_blank" style="color: #0070ba; font-size: 13px; font-weight: bold;"> or Donate via PayPal </a></p>
      <img src="https://mywebsite.com/media/images/qris_mywebsite.png"
           alt="QRIS Support"
           style="width:150px;border-radius:8px;border:2px solid #e94560;display:block;"/>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# METHODOLOGY NOTE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="spss-note">
  <b>Normality-based auto-selection:</b>
  All tests automatically evaluate normality using both the
  <b>Shapiro-Wilk test</b> and the
  <b>Kolmogorov-Smirnov test with Lilliefors significance correction</b>.
  The primary criterion is determined by Total N:
  Shapiro-Wilk for Total N &lt; 50 (superior power in small samples);
  Kolmogorov-Smirnov for Total N &ge; 50.
  If the normality assumption is violated, the appropriate non-parametric
  equivalent is applied automatically.
  References: Razali &amp; Wah (2011); Shapiro &amp; Wilk (1965);
  Lilliefors (1967); Field (2018).
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGES MAP
# ══════════════════════════════════════════════════════════════════════════════
# Maps test names to their Streamlit page paths
PAGES = {
    "One-Sample T-Test":         "pages/1_t_tests.py",
    "Paired-Sample T-Test":      "pages/1_t_tests.py",
    "Independent-Sample T-Test": "pages/1_t_tests.py",
    "One-Way ANOVA":             "pages/2_anova.py",
    "Factorial ANOVA":           "pages/2_anova.py",
    "Repeated Measures ANOVA":   "pages/2_anova.py",
    "Mixed ANOVA":               "pages/2_anova.py",
    "One-Way ANCOVA":            "pages/3_ancova.py",
    "Factorial ANCOVA":         "pages/3_ancova.py",
    "Repeated Measures ANCOVA": "pages/3_ancova.py",
    "Mixed ANCOVA":             "pages/3_ancova.py",
    "MANCOVA":                  "pages/3_ancova.py",
    "Linear Regression":        "pages/4_regression.py",
    "Multiple Regression":      "pages/4_regression.py",
    "Bivariate Correlation":    "pages/5_correlation.py",
    "Reliability Analysis":     "pages/6_reliability.py",
}

ACTIVE_TESTS = {k for k, v in PAGES.items() if v is not None}

# ══════════════════════════════════════════════════════════════════════════════
# TEST CARDS — PER CATEGORY
# ══════════════════════════════════════════════════════════════════════════════
for cat_name, cat_info in CATEGORIES.items():
    # Category header
    st.markdown(
        f'<div class="cat-hdr">'
        f'{cat_info["icon"]} {cat_name}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="cat-desc">{cat_info["desc"]}</p>',
        unsafe_allow_html=True,
    )

    tests = cat_info["tests"]
    cols  = st.columns(len(tests))

    for col, test_name in zip(cols, tests):
        card  = get_card_content(test_name)
        active = test_name in ACTIVE_TESTS

        with col:
            # Card HTML
            coming_cls = "" if active else " coming-soon"
            st.markdown(
                f'<div class="test-card{coming_cls}">'
                f'<span class="card-icon">{card["icon"]}</span>'
                f'<div class="card-title">{test_name}</div>'
                f'<div class="card-short">{card["short"]}</div>'
                f'<div class="card-use">'
                f'<b>Use when:</b> {card["use_when_short"]}'
                f'</div>'
                f'<div>'
                f'<span class="card-np">&#8614; {card["nonparam"]}</span>'
                f'</div>'
                f'<div style="margin-top:.5rem;">'
                f'<span class="card-es">&#963; {card["effect_size"]}</span>'
                f'</div>'
                + ('' if active else
                   '<div class="coming-tag">&#128679; Coming Soon</div>')
                + '</div>',
                unsafe_allow_html=True,
            )

            # Navigate button (only for active tests)
            if active:
                page_path = PAGES[test_name]
                if st.button(
                    f"Open {test_name.split()[0]} \u2192",
                    key=f"btn_{test_name}",
                    use_container_width=True,
                ):
                    st.session_state["selected_test"] = test_name
                    st.switch_page(page_path)

    st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# METHODOLOGY FEATURES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### &#128300; What Makes This App Different from SPSS?")

st.markdown("""
<div class="method-grid">
  <div class="method-item">
    <b>&#10003; Normality auto-select</b><br/>
    SW for n &lt; 50, KS Lilliefors for n &ge; 50. Decision based on Total N.
  </div>
  <div class="method-item">
    <b>&#10003; Cohen&#39;s d</b><br/>
    Parametric effect size for all t-tests. Not in SPSS by default.
  </div>
  <div class="method-item">
    <b>&#10003; Rank-biserial r</b><br/>
    Non-parametric effect size with 95% bootstrap CI (2,000 resamples).
  </div>
  <div class="method-item">
    <b>&#10003; Power analysis</b><br/>
    Post-hoc power via non-central t/F-distribution + min n for power = .80.
  </div>
  <div class="method-item">
    <b>&#10003; APA 7th write-up</b><br/>
    Automatically generated, publication-ready write-up per analysis.
  </div>
  <div class="method-item">
    <b>&#10003; HTML + CSV export</b><br/>
    Offline report with embedded plots. CSV readable by any software.
  </div>
  <div class="method-item">
    <b>&#10003; Levene center=mean</b><br/>
    SPSS-exact Levene&#39;s test. Welch correction applied automatically.
  </div>
  <div class="method-item">
    <b>&#10003; Wilcoxon Z ties-corrected</b><br/>
    SPSS-exact Z with ties correction. Mann-Whitney U in SPSS format.
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#94a3b8;font-size:.76rem;'
    'line-height:1.8;padding:.5rem 0;">'
    'Inferential Statistics by MA &nbsp;&middot;&nbsp; '
    'SPSS-equivalent output &nbsp;&middot;&nbsp; '
    'Academic English &nbsp;&middot;&nbsp; '
    'Shapiro-Wilk + KS Lilliefors &nbsp;&middot;&nbsp; '
    'Levene center\u2009=\u2009mean &nbsp;&middot;&nbsp; '
    'Wilcoxon Z ties-corrected &nbsp;&middot;&nbsp; '
    'Mann-Whitney U SPSS-exact &nbsp;&middot;&nbsp; '
    'Cohen\u2019s d &nbsp;&middot;&nbsp; '
    'Rank-biserial r + Bootstrap CI &nbsp;&middot;&nbsp; '
    'Power Analysis<br/>'
    'References: Cohen (1988) &middot; Field (2018) &middot; '
    'Razali &amp; Wah (2011) &middot; Lilliefors (1967) &middot; '
    'Kerby (2014) &middot; Efron &amp; Tibshirani (1993)'
    '</div>',
    unsafe_allow_html=True,
)
