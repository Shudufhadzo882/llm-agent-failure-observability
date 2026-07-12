import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Risk & Compliance Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- THEME STATE ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# --- DESIGN SYSTEM CSS ---
# Zinc/shadcn inspired theme colors
css_vars = f"""
<style>
:root {{
    --bg: {"#09090b" if IS_DARK else "#ffffff"};
    --bg-subtle: {"#0c0c0f" if IS_DARK else "#f9fafb"};
    --card: {"#0c0c0f" if IS_DARK else "#ffffff"};
    --card-hover: {"#131316" if IS_DARK else "#f4f4f5"};
    --border: {"#1e1e24" if IS_DARK else "#e4e4e7"};
    --border-subtle: {"#16161a" if IS_DARK else "#f0f0f2"};
    --text: {"#fafafa" if IS_DARK else "#09090b"};
    --text-muted: #71717a;
    --text-dim: {"#52525b" if IS_DARK else "#a1a1aa"};
    --accent: #2563eb;
    --accent-muted: #1d4ed8;
    --green: {"#22c55e" if IS_DARK else "#16a34a"};
    --green-muted: {"rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"};
    --red: {"#ef4444" if IS_DARK else "#dc2626"};
    --red-muted: {"rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"};
    --amber: {"#f59e0b" if IS_DARK else "#d97706"};
    --amber-muted: {"rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"};
    --shadow: {"none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"};
    --radius: 10px;
}}

/* Hide Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

/* Global Styling */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}
.block-container {{
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}}

/* Layout Spacing */
[data-testid="stHorizontalBlock"] {{
    gap: 1.25rem !important;
}}

/* Tabs Styling (pill-style) */
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.835rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.1rem !important;
    border: 1px solid transparent !important;
    border-radius: 7px !important;
    transition: all 0.2s ease !important;
}}
button[data-baseweb="tab"]:hover {{
    color: var(--text) !important;
    background: var(--card-hover) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 6px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    margin-bottom: 1.5rem !important;
}}

/* KPI Cards */
.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow);
}}
.metric-label {{
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.metric-value {{
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    margin-top: 0.25rem;
}}
.metric-delta {{
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.4rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}}
.delta-up {{ color: var(--green); background: var(--green-muted); }}
.delta-down {{ color: var(--red); background: var(--red-muted); }}
.delta-warn {{ color: var(--amber); background: var(--amber-muted); }}

/* Chart Wrapper */
.chart-wrap {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem 0.8rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
}}
.chart-title {{
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
}}
.chart-subtitle {{
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-bottom: 0.9rem;
}}

/* Data Tables */
.table-container {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow);
    overflow-x: auto;
}}
.data-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.82rem;
}}
.data-table th {{
    text-align: left;
    padding: 0.75rem 1rem;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border);
}}
.data-table td {{
    padding: 0.8rem 1rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
}}
.data-table tr:hover td {{
    background-color: var(--card-hover);
}}
.data-table tr:last-child td {{
    border-bottom: none;
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
    text-align: center;
}}
.badge-green {{ color: var(--green); background: var(--green-muted); }}
.badge-red {{ color: var(--red); background: var(--red-muted); }}
.badge-amber {{ color: var(--amber); background: var(--amber-muted); }}
.badge-blue {{ color: var(--accent); background: rgba(37,99,235,0.1); }}

/* Inspector Detail Block */
.detail-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}}
.detail-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}
.detail-content {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    white-space: pre-wrap;
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
    color: var(--text);
}}
.detail-text {{
    font-size: 0.875rem;
    line-height: 1.5;
    color: var(--text);
}}

/* Custom button overrides to match theme */
div.stButton > button {{
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 0.8rem !important;
    transition: all 0.2s ease !important;
}}
div.stButton > button:hover {{
    border-color: var(--accent) !important;
    background-color: var(--card-hover) !important;
}}
</style>
"""
st.markdown(css_vars, unsafe_allow_html=True)

# --- UTILITY HELPERS ---
def get_db_connection():
    return sqlite3.connect("ai_observability.db")

def metric_card(label, value, delta=None, delta_type="up"):
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "→")
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# Plotly styling dictionary based on current theme state
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=11),
    margin=dict(l=0, r=0, t=25, b=0),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        tickfont=dict(size=10, color="#71717a"),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
        tickfont=dict(size=10, color="#71717a"),
    ),
)

# --- LOAD DATA ---
@st.cache_data
def load_data_from_db():
    conn = get_db_connection()
    
    # Query evaluations
    query_evals = """
    SELECT 
        fe.task_id, 
        dd.domain_name as domain, 
        fe.difficulty, 
        df1.failure_name as true_failure, 
        df2.failure_name as pred_failure, 
        ds1.severity_level as true_severity, 
        ds2.severity_level as pred_severity,
        fe.is_accurate_match,
        fe.eval_notes
    FROM fact_evaluations fe
    LEFT JOIN dim_domains dd ON fe.domain_id = dd.domain_id
    LEFT JOIN dim_failures df1 ON fe.true_failure_id = df1.failure_id
    LEFT JOIN dim_failures df2 ON fe.pred_failure_id = df2.failure_id
    LEFT JOIN dim_severities ds1 ON fe.true_severity_id = ds1.severity_id
    LEFT JOIN dim_severities ds2 ON fe.pred_severity_id = ds2.severity_id
    """
    df_evals = pd.read_sql_query(query_evals, conn)
    
    # Query full tasks
    df_tasks = pd.read_sql_query("SELECT * FROM dim_tasks", conn)
    
    conn.close()
    return df_evals, df_tasks

try:
    df_evals, df_tasks = load_data_from_db()
except Exception as e:
    st.error(f"Error loading database: {e}. Please ensure you've executed the evaluation pipeline and populated 'ai_observability.db'.")
    st.stop()

# --- HEADER SECTION ---
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <span style="font-size: 1.35rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em;">◆ AI Risk & Compliance Observability</span>
        <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.15rem;">LLM Agent Failure Mode Analysis & Judge Audit Log</div>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

# --- NAVIGATION TABS ---
tab_overview, tab_logs, tab_explorer = st.tabs([
    "📊 System Overview",
    "🔎 Failure Logs & Audit",
    "🗄️ Database Explorer"
])

# ==========================================
# TAB 1: SYSTEM OVERVIEW
# ==========================================
with tab_overview:
    # 1. KPI Cards Row
    total_logs = len(df_evals)
    accurate_matches = df_evals['is_accurate_match'].sum()
    accuracy_pct = (accurate_matches / total_logs) * 100 if total_logs > 0 else 0
    mismatches = total_logs - accurate_matches
    
    # Severity calculations
    high_critical_count = len(df_evals[df_evals['true_severity'].isin(['High', 'Critical'])])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Logs Analyzed", f"{total_logs}", delta="Log Count", delta_type="up")
    with c2:
        metric_card("Classifier Accuracy", f"{accuracy_pct:.1f}%", delta="vs Ground Truth", delta_type="up" if accuracy_pct >= 80 else "warn")
    with c3:
        metric_card("Mismatches Detected", f"{mismatches}", delta="Needs Refinement", delta_type="warn" if mismatches > 0 else "up")
    with c4:
        metric_card("High/Critical Risk", f"{high_critical_count}", delta="Requires Review", delta_type="down" if high_critical_count > 0 else "up")
        
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # 2. Charts Row
    ch_col1, ch_col2 = st.columns(2)
    
    with ch_col1:
        # Plot 1: Failure Distribution by Category (True vs Predicted)
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Failure Mode Distributions</div>
            <div class="chart-subtitle">Comparison of true (ground truth) vs predicted failure types</div>
        """, unsafe_allow_html=True)
        
        true_counts = df_evals['true_failure'].value_counts().reset_index()
        true_counts.columns = ['Failure Mode', 'Count']
        true_counts['Type'] = 'Actual'
        
        pred_counts = df_evals['pred_failure'].value_counts().reset_index()
        pred_counts.columns = ['Failure Mode', 'Count']
        pred_counts['Type'] = 'Predicted'
        
        chart_df = pd.concat([true_counts, pred_counts])
        
        fig_cat = px.bar(
            chart_df,
            x='Count',
            y='Failure Mode',
            color='Type',
            barmode='group',
            orientation='h',
            color_discrete_map={'Actual': '#2563eb', 'Predicted': '#a1a1aa' if IS_DARK else '#71717a'},
            height=300
        )
        fig_cat.update_layout(
            **PLOT_LAYOUT,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with ch_col2:
        # Plot 2: Severity Distribution
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Severity Level Risk Breakdown</div>
            <div class="chart-subtitle">Volumetric counts of agent failures categorized by severity levels</div>
        """, unsafe_allow_html=True)
        
        severity_order = ['Low', 'Medium', 'High', 'Critical']
        sev_counts = df_evals['true_severity'].value_counts().reindex(severity_order).fillna(0).reset_index()
        sev_counts.columns = ['Severity', 'Count']
        
        fig_sev = px.bar(
            sev_counts,
            x='Severity',
            y='Count',
            color='Severity',
            color_discrete_map={
                'Low': '#22c55e',
                'Medium': '#3b82f6',
                'High': '#f59e0b',
                'Critical': '#ef4444'
            },
            height=300
        )
        fig_sev.update_layout(**PLOT_LAYOUT, showlegend=False)
        st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    # 3. Third Row: Domain Breakdown
    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">Failures and Classification Matches by Domain</div>
        <div class="chart-subtitle">Comparison of correct matches and classifier failures per domain</div>
    """, unsafe_allow_html=True)
    
    domain_df = df_evals.groupby(['domain', 'is_accurate_match']).size().reset_index(name='count')
    domain_df['Match Status'] = domain_df['is_accurate_match'].map({1: 'Match', 0: 'Mismatch'})
    
    fig_dom = px.bar(
        domain_df,
        x='domain',
        y='count',
        color='Match Status',
        barmode='stack',
        color_discrete_map={'Match': '#22c55e', 'Mismatch': '#ef4444'},
        height=280
    )
    fig_dom.update_layout(
        **PLOT_LAYOUT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig_dom, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: FAILURE LOGS & AUDIT
# ==========================================
with tab_logs:
    st.markdown("<h4 style='font-size: 1rem; font-weight:600; margin-bottom:0.5rem;'>Audit Trail & Filtering</h4>", unsafe_allow_html=True)
    
    # 1. Filters Row
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        domains_list = ["All"] + list(df_evals['domain'].unique())
        sel_domain = st.selectbox("Filter Domain", domains_list)
    with f_col2:
        difficulties_list = ["All"] + list(df_evals['difficulty'].unique())
        sel_diff = st.selectbox("Filter Difficulty", difficulties_list)
    with f_col3:
        sel_status = st.selectbox("Filter Match Status", ["All", "Match", "Mismatch"])
    with f_col4:
        search_query = st.text_input("Search Logs Keyword", "")
        
    # Apply filters
    filtered_df = df_evals.copy()
    if sel_domain != "All":
        filtered_df = filtered_df[filtered_df['domain'] == sel_domain]
    if sel_diff != "All":
        filtered_df = filtered_df[filtered_df['difficulty'] == sel_diff]
    if sel_status == "Match":
        filtered_df = filtered_df[filtered_df['is_accurate_match'] == 1]
    elif sel_status == "Mismatch":
        filtered_df = filtered_df[filtered_df['is_accurate_match'] == 0]
        
    # Search functionality
    if search_query:
        # Merge task text details to search them
        merged_search = filtered_df.merge(df_tasks, on='task_id')
        search_mask = (
            merged_search['prompt'].str.contains(search_query, case=False) |
            merged_search['context'].str.contains(search_query, case=False) |
            merged_search['eval_notes'].str.contains(search_query, case=False) |
            merged_search['task_id'].str.contains(search_query, case=False)
        )
        filtered_df = filtered_df[filtered_df['task_id'].isin(merged_search[search_mask]['task_id'])]

    # 2. Render Custom HTML Table
    table_rows_html = ""
    for idx, row in filtered_df.iterrows():
        # Match badge
        badge_cls = "badge-green" if row['is_accurate_match'] == 1 else "badge-red"
        badge_text = "Match" if row['is_accurate_match'] == 1 else "Mismatch"
        badge_html = f'<span class="badge {badge_cls}">{badge_text}</span>'
        
        # Predicted Failure warning style on mismatch
        pred_fail_style = "" if row['is_accurate_match'] == 1 else 'style="color: var(--red); font-weight:600;"'
        
        # Severity Badge
        sev_cls = "badge-blue"
        if row['true_severity'] == "Critical": sev_cls = "badge-red"
        elif row['true_severity'] == "High": sev_cls = "badge-amber"
        elif row['true_severity'] == "Medium": sev_cls = "badge-blue"
        else: sev_cls = "badge-green"
        
        sev_html = f'<span class="badge {sev_cls}">{row["true_severity"]}</span>'
        
        table_rows_html += f"""
        <tr>
            <td style="font-family: 'JetBrains Mono', monospace; font-weight:600;">{row['task_id']}</td>
            <td>{row['domain']}</td>
            <td>{row['difficulty']}</td>
            <td>{row['true_failure']}</td>
            <td {pred_fail_style}>{row['pred_failure']}</td>
            <td>{sev_html}</td>
            <td>{badge_html}</td>
        </tr>
        """
        
    if not table_rows_html:
        table_rows_html = "<tr><td colspan='7' style='text-align:center; color:var(--text-muted);'>No failure logs found matching the filter criteria.</td></tr>"
        
    table_full_html = f"""
    <div class="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Task ID</th>
                    <th>Domain</th>
                    <th>Difficulty</th>
                    <th>True Failure Type</th>
                    <th>Predicted Failure Type</th>
                    <th>True Severity</th>
                    <th>Match Status</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_full_html, unsafe_allow_html=True)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # 3. Interactive Detail Inspector
    st.markdown("<h4 style='font-size: 1rem; font-weight:600; margin-bottom:0.5rem;'>🔎 Detailed Task Inspector</h4>", unsafe_allow_html=True)
    
    if len(filtered_df) > 0:
        inspect_task_list = list(filtered_df['task_id'])
        selected_task_id = st.selectbox("Select a Task ID to inspect details:", inspect_task_list)
        
        # Fetch detailed texts
        task_text_row = df_tasks[df_tasks['task_id'] == selected_task_id].iloc[0]
        eval_row = df_evals[df_evals['task_id'] == selected_task_id].iloc[0]
        
        # Display Details layout
        ins_col1, ins_col2 = st.columns(2)
        
        with ins_col1:
            st.markdown(f"""
            <div class="detail-card">
                <div class="detail-label">Task ID</div>
                <div style="font-size: 1.1rem; font-weight: 700; font-family: 'JetBrains Mono'; margin-bottom: 0.75rem;">{selected_task_id}</div>
                
                <div class="detail-label">Prompt</div>
                <div class="detail-content">{task_text_row['prompt']}</div>
                
                <div style="margin-top: 1rem;" class="detail-label">Available Context</div>
                <div class="detail-content" style="max-height: 250px;">{task_text_row['context']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with ins_col2:
            st.markdown(f"""
            <div class="detail-card">
                <div class="detail-label">Expected Answer (Ground Truth)</div>
                <div class="detail-content" style="border-left: 3px solid var(--green); background: var(--green-muted); max-height: 150px;">{task_text_row['expected_answer']}</div>
                
                <div style="margin-top: 1rem;" class="detail-label">Flawed Agent Answer</div>
                <div class="detail-content" style="border-left: 3px solid var(--red); background: var(--red-muted); max-height: 150px;">{task_text_row['agent_answer']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Judge Notes box
            match_cls = "badge-green" if eval_row['is_accurate_match'] == 1 else "badge-red"
            match_text = "Match" if eval_row['is_accurate_match'] == 1 else "Mismatch"
            
            st.markdown(f"""
            <div class="detail-card" style="border-left: 4px solid {"var(--accent)" if eval_row['is_accurate_match'] == 1 else "var(--amber)"};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div class="detail-label" style="margin-bottom: 0;">🤖 Judge Analysis Rationale</div>
                    <span class="badge {match_cls}">{match_text}</span>
                </div>
                <div style="margin-bottom: 0.5rem; font-size: 0.8rem;">
                    <strong>Predicted Category:</strong> <code style="font-family:'JetBrains Mono';">{eval_row['pred_failure']}</code><br>
                    <strong>Predicted Severity:</strong> <code style="font-family:'JetBrains Mono';">{eval_row['pred_severity']}</code>
                </div>
                <div class="detail-text">{eval_row['eval_notes']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Filter selection returned zero logs. Reset filters to inspect tasks.")

# ==========================================
# TAB 3: DATABASE EXPLORER
# ==========================================
with tab_explorer:
    st.markdown("<h4 style='font-size: 1rem; font-weight:600; margin-bottom:0.5rem;'>🗄️ SQLite Raw Data Inspection</h4>", unsafe_allow_html=True)
    
    conn = get_db_connection()
    tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    sel_table = st.selectbox("Select SQLite Table to inspect", tables)
    
    if sel_table:
        table_df = pd.read_sql_query(f"SELECT * FROM {sel_table}", conn)
        st.markdown(f"<div style='font-size:0.75rem; color:var(--text-muted); margin-bottom:0.5rem;'>Showing {len(table_df)} rows from table '{sel_table}'</div>", unsafe_allow_html=True)
        st.dataframe(table_df, use_container_width=True)
        
    conn.close()
