"""
utils/tables.py
===============
HTML table builder for statistical output in Streamlit UI.
Returns an HTML string rendered via st.markdown(unsafe_allow_html=True).
"""


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
