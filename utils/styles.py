"""
utils/styles.py
===============
Centralised CSS styles for the Reliability Toolkit (Internal Consistency
and Inter-Rater Agreement). All styles are defined as string constants
and injected via st.markdown().

Usage:
    from utils.styles import load_css
    st.markdown(load_css(), unsafe_allow_html=True)
"""


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE FONTS IMPORT
# ══════════════════════════════════════════════════════════════════════════════

FONTS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
"""


# ══════════════════════════════════════════════════════════════════════════════
# BASE
# ══════════════════════════════════════════════════════════════════════════════

BASE = """
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
section[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
button[kind="header"] { display: none !important; }
"""


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

HEADER = """
.main-hdr {
    background: linear-gradient(120deg, #0a0a0a 0%, #1a1a2e 40%, #16213e 100%);
    padding: 2rem 2.4rem;
    border-radius: 14px;
    margin-bottom: 1.8rem;
    border-left: 5px solid #e94560;
    box-shadow: 0 8px 32px rgba(233, 69, 96, .15);
}
.main-hdr h1 {
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 .4rem 0;
    letter-spacing: -.4px;
}
.main-hdr p {
    color: #94a3b8;
    margin: 0;
    font-size: .92rem;
}
.badge {
    display: inline-block;
    background: #e94560;
    color: #fff;
    font-size: .7rem;
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 8px;
    font-weight: 600;
    vertical-align: middle;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# HOMEPAGE CARDS
# ══════════════════════════════════════════════════════════════════════════════

CARDS = """
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.test-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, .05);
    transition: box-shadow .2s, transform .2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.test-card:hover {
    box-shadow: 0 8px 24px rgba(233, 69, 96, .12);
    transform: translateY(-2px);
}
.test-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: #e94560;
    border-radius: 4px 0 0 4px;
}
.test-card h4 {
    color: #1a1a2e;
    font-size: .95rem;
    font-weight: 700;
    margin: 0 0 .5rem;
}
.test-card p {
    color: #475569;
    font-size: .82rem;
    margin: 0 0 .8rem;
    line-height: 1.6;
}
.test-card .nonparam-tag {
    display: inline-block;
    background: #f1f5f9;
    color: #64748b;
    font-size: .7rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
}
.category-hdr {
    font-size: .78rem;
    font-weight: 700;
    color: #e94560;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 1.6rem 0 .8rem;
    padding-bottom: .4rem;
    border-bottom: 2px solid #f1f5f9;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION PANEL
# ══════════════════════════════════════════════════════════════════════════════

CONFIG = """
.cfg-panel {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, .05);
}
.cfg-panel h3 {
    margin: 0 0 1rem;
    font-size: .95rem;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 2px solid #e94560;
    padding-bottom: .5rem;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# SECTION TITLES & SUB-TITLES
# ══════════════════════════════════════════════════════════════════════════════

TITLES = """
.sec-title {
    background: linear-gradient(90deg, #1a1a2e, #16213e);
    color: #e2e8f0;
    padding: 9px 16px;
    border-radius: 6px 6px 0 0;
    font-weight: 600;
    font-size: .84rem;
    letter-spacing: .6px;
    margin-top: 1.4rem;
    font-family: 'DM Mono', monospace;
    border-bottom: 2px solid #e94560;
}
.sub-title {
    background: #f1f5f9;
    color: #1a1a2e;
    padding: 7px 14px;
    border-radius: 6px;
    font-weight: 600;
    font-size: .82rem;
    margin: 1rem 0 .4rem;
    border-left: 3px solid #e94560;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# STATISTICAL OUTPUT TABLES
# ══════════════════════════════════════════════════════════════════════════════

TABLES = """
.stat-tbl-wrap {
    overflow-x: auto;
    margin-bottom: .4rem;
}
.stat-tbl {
    font-family: 'DM Mono', monospace;
    font-size: .77rem;
    border-collapse: collapse;
    width: 100%;
    min-width: 400px;
}
.stat-tbl th {
    background: #1a1a2e;
    color: #e2e8f0;
    padding: 7px 12px;
    text-align: center;
    font-weight: 600;
    border: 1px solid #334155;
    font-size: .74rem;
    white-space: nowrap;
}
.stat-tbl td {
    padding: 5px 12px;
    border: 1px solid #e2e8f0;
    text-align: right;
    color: #1e293b;
    white-space: nowrap;
    background: #fff;
}
.stat-tbl tr:nth-child(even) td {
    background: #f8fafc;
}
.stat-tbl td.left {
    text-align: left;
    font-weight: 500;
    background: #f1f5f9 !important;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# METRIC CARDS
# ══════════════════════════════════════════════════════════════════════════════

METRICS = """
.metric-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: .9rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .05);
}
.metric-val {
    font-size: 1.45rem;
    font-weight: 700;
    color: #1a1a2e;
    font-family: 'DM Mono', monospace;
}
.metric-lbl {
    font-size: .7rem;
    color: #64748b;
    margin-top: .25rem;
    text-transform: uppercase;
    letter-spacing: .6px;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# DECISION BANNERS
# ══════════════════════════════════════════════════════════════════════════════

BANNERS = """
.decision-banner {
    padding: 1rem 1.4rem;
    border-radius: 10px;
    margin: 1rem 0;
    font-size: .9rem;
    font-weight: 600;
}
.decision-banner.use-param {
    background: #dcfce7;
    color: #14532d;
    border: 1px solid #86efac;
}
.decision-banner.use-nonparam {
    background: #ffedd5;
    color: #7c2d12;
    border: 1px solid #fdba74;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# INTERPRETATION BOXES
# ══════════════════════════════════════════════════════════════════════════════

INTERP = """
.interp-box {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border-left: 4px solid #0284c7;
    padding: 1rem 1.2rem;
    border-radius: 0 10px 10px 0;
    margin: .7rem 0;
    font-size: .87rem;
    line-height: 1.8;
    color: #1e293b;
}
.interp-box b { color: #0284c7; }
.interp-box.sig {
    border-left-color: #16a34a;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}
.interp-box.sig b { color: #16a34a; }
.interp-box.nonsig {
    border-left-color: #dc2626;
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
}
.interp-box.nonsig b { color: #dc2626; }
"""


# ══════════════════════════════════════════════════════════════════════════════
# ALERT & INFO BOXES
# ══════════════════════════════════════════════════════════════════════════════

ALERTS = """
.warn-box {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: .7rem 1rem;
    border-radius: 0 6px 6px 0;
    font-size: .82rem;
    color: #92400e;
    margin: .4rem 0;
}
.info-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: .7rem 1rem;
    border-radius: 0 6px 6px 0;
    font-size: .82rem;
    color: #1e40af;
    margin: .4rem 0;
}
.norm-rec-box {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border-left: 4px solid #0284c7;
    padding: .8rem 1rem;
    border-radius: 0 8px 8px 0;
    font-size: .82rem;
    color: #0c4a6e;
    margin: .5rem 0;
    line-height: 1.7;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# TEXT UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

TEXT = """
.pass  { color: #16a34a; font-weight: 700; }
.fail  { color: #dc2626; font-weight: 700; }
.note-txt {
    font-size: .74rem;
    color: #64748b;
    font-style: italic;
    margin-top: .3rem;
    line-height: 1.6;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOADER FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def load_css():
    """
    Return the complete CSS string for injection via st.markdown().

    Usage:
        import streamlit as st
        from utils.styles import load_css
        st.markdown(load_css(), unsafe_allow_html=True)
    """
    all_css = (
        FONTS
        + BASE
        + HEADER
        + CARDS
        + CONFIG
        + TITLES
        + TABLES
        + METRICS
        + BANNERS
        + INTERP
        + ALERTS
        + TEXT
    )
    return f"<style>{all_css}</style>"


def load_page_css():
    """
    Return CSS for the analysis pages only (excludes homepage card
    styles). Use this in views/internalconsistency.py and
    views/interrateragreement.py.
    """
    page_css = (
        FONTS
        + BASE
        + HEADER
        + CONFIG
        + TITLES
        + TABLES
        + METRICS
        + BANNERS
        + INTERP
        + ALERTS
        + TEXT
    )
    return f"<style>{page_css}</style>"
