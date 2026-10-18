"""
app.py
======
Entry point for the Reliability Toolkit. Shows a two-card landing page
and registers the two analyses as separate routed pages:
    /internalconsistency
    /interrateragreement
"""

import streamlit as st

from utils.styles import load_css


def home():
    st.set_page_config(
        page_title="Reliability Toolkit",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(load_css(), unsafe_allow_html=True)

    st.markdown(
        """
        <div class="main-hdr">
          <h1>&#129514; Reliability Toolkit</h1>
          <p>Choose an analysis below to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="test-card">
              <h4>&#128202; Internal Consistency</h4>
              <p>For scales made of multiple items measuring one construct.
              Computes Cronbach&#39;s &alpha;, KR-20 / KR-21, Split-Half
              reliability, Guttman&#39;s &lambda; (6 forms), McDonald&#39;s
              &omega; (model-implied, observed, and hierarchical), and
              ICC(C,k) &mdash; plus full item-level diagnostics.</p>
              <span class="nonparam-tag">Cronbach&#39;s &alpha; &middot; KR-20 &middot; McDonald&#39;s &omega; &middot; ICC</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "views/internalconsistency.py",
            label="Open Internal Consistency",
            icon="➡️",
            use_container_width=True,
        )

    with col2:
        st.markdown(
            """
            <div class="test-card">
              <h4>&#129309; Inter-Rater Agreement</h4>
              <p>For agreement between two or more raters/judges scoring
              the same units. Computes Percentage Agreement, Cohen&#39;s /
              Fleiss&#39; &kappa;, Gwet&#39;s AC1 / AC2, Scott&#39;s &pi;,
              the Brennan-Prediger coefficient, ICC (all six forms),
              Lin&#39;s CCC, and Krippendorff&#39;s &alpha;.</p>
              <span class="nonparam-tag">Cohen&#39;s/Fleiss&#39; &kappa; &middot; Gwet&#39;s AC1/AC2 &middot; Krippendorff&#39;s &alpha;</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "views/interrateragreement.py",
            label="Open Inter-Rater Agreement",
            icon="➡️",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


home_page = st.Page(home, title="Home", icon="🏠", default=True)
ic_page = st.Page(
    "views/internalconsistency.py",
    title="Internal Consistency",
    icon="📊",
    url_path="internalconsistency",
)
ira_page = st.Page(
    "views/interrateragreement.py",
    title="Inter-Rater Agreement",
    icon="🤝",
    url_path="interrateragreement",
)

# Callable-based pages (like `home_page` here) have no file-path identity,
# so sub-pages cannot link back to them with st.page_link("app.py", ...).
# Stash the actual Page object in session_state so every page can retrieve
# the same object and pass it to st.page_link() directly.
st.session_state["_home_page"] = home_page

pg = st.navigation([home_page, ic_page, ira_page], position="hidden")
pg.run()
