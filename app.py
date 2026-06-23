import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Player Auction Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS — light minimalist theme, gold/pitch-green accents ──────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg: #FAF7F2;
        --card: #F3EAE4;
        --ink: #241414;
        --muted: #7A6660;
        --burgundy: #6E1423;
        --burgundy-soft: #E8D2D6;
        --burgundy-dim: #9C5A66;
        --green: #2D6A4F;
        --gold: #B8923D;
        --line: #E0D2CC;
    }

    /* ── Force base text color everywhere, overriding Streamlit's dark-theme default ── */
    html, body, [class*="css"], [class*="st-"],
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label,
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    [data-testid="stSidebar"] *, [data-testid="stAppViewContainer"] * {
        color: var(--ink) !important;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg);
    }

    .stApp { background: var(--bg) !important; }
    [data-testid="stAppViewContainer"] { background: var(--bg) !important; }
    [data-testid="stHeader"] { background: var(--bg) !important; }

    [data-testid="stSidebar"] {
        background: var(--card) !important;
        border-right: 1px solid var(--line);
    }

    /* Sidebar section labels (radio/multiselect/slider widget labels) */
    [data-testid="stSidebar"] label, [data-testid="stWidgetLabel"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--burgundy) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700 !important;
    }

    /* Sidebar bold markdown headers like "SELECT MODE" */
    [data-testid="stSidebar"] strong {
        color: var(--burgundy) !important;
        font-weight: 700 !important;
    }

    /* Radio button option text */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stRadio"] label p, [data-testid="stRadio"] div {
        color: var(--ink) !important;
        text-transform: none !important;
        font-weight: 500 !important;
    }

    h1, h2, h3 {
        font-family: 'Libre Caslon Text', serif !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
    }

    h4, h5 {
        font-family: 'Inter', sans-serif !important;
        color: var(--ink) !important;
    }

    [data-testid="stMetric"] {
        background: var(--card) !important;
        border: 1px solid var(--line);
        border-top: 3px solid var(--burgundy);
        border-radius: 4px;
        padding: 14px !important;
    }

    [data-testid="stMetricLabel"] p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.62rem !important;
        color: var(--muted) !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Libre Caslon Text', serif !important;
        color: var(--burgundy) !important;
    }

    /* Signature element: stitched-seam divider, evokes cricket ball stitching */
    hr {
        border: none !important;
        border-top: 2px dashed var(--burgundy) !important;
        opacity: 0.5;
        margin: 1.4rem 0 !important;
    }

    .role-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    [data-testid="stDataFrame"] { border: 1px solid var(--line); }
    [data-testid="stDataFrame"] * { color: var(--ink) !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--card) !important;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [data-baseweb="tab"] p {
        color: var(--muted) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--burgundy-soft) !important;
        border-bottom: 2px solid var(--burgundy);
    }
    .stTabs [aria-selected="true"] p { color: var(--burgundy) !important; }

    .stButton button {
        border-radius: 4px;
        border: 1px solid var(--line);
        font-weight: 600;
        color: var(--ink) !important;
        background: #fff !important;
    }
    .stButton button p { color: var(--ink) !important; }

    .stButton button[kind="primary"] {
        background-color: var(--burgundy) !important;
        border-color: var(--burgundy) !important;
    }
    .stButton button[kind="primary"] p { color: #fff !important; }

    /* Multiselect tags ("Batter ×", player chips) */
    [data-baseweb="tag"] {
        background-color: var(--burgundy) !important;
        color: #fff !important;
    }
    [data-baseweb="tag"] span { color: #fff !important; }

    /* ── Selectbox / Multiselect input field (the closed box showing current value) ── */
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: var(--line) !important;
    }
    [data-baseweb="select"] * { color: var(--ink) !important; }

    /* ── Dropdown popover/listbox (opens on click — this was rendering dark-on-dark) ── */
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    [data-baseweb="menu"] li,
    ul[role="listbox"] li,
    [role="option"] {
        background-color: #ffffff !important;
        color: var(--ink) !important;
    }
    [role="option"] * { color: var(--ink) !important; }
    /* Hover / highlighted option */
    [role="option"]:hover, [aria-selected="true"][role="option"] {
        background-color: var(--burgundy-soft) !important;
        color: var(--burgundy) !important;
    }
    [aria-selected="true"][role="option"] * { color: var(--burgundy) !important; }

    /* Search/filter text typed into select boxes */
    [data-baseweb="select"] input { color: var(--ink) !important; }

    /* Slider numbers and track */
    [data-testid="stSlider"] [data-testid="stTickBar"] { color: var(--muted) !important; }
    [data-testid="stThumbValue"] { color: var(--burgundy) !important; font-weight: 700; }

    /* Captions */
    [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }

    [data-testid="stMetricDelta"] svg { display: none; }
</style>
""", unsafe_allow_html=True)

# Shared chart theme tokens — used across every Plotly figure for visual consistency
CHART_BG = "#FAF7F2"
CHART_PAPER = "rgba(0,0,0,0)"
CHART_GRID = "#E0D2CC"
CHART_FONT = dict(family="Inter, sans-serif", color="#241414")
BURGUNDY = "#6E1423"
GOLD = "#B8923D"
GREEN = "#2D6A4F"
RED = "#9B2335"
MUTED = "#7A6660"
PLAYER_PALETTE = [BURGUNDY, GOLD, GREEN, "#3B5BA5", "#7B4B94", "#C97B30"]

def style_fig(fig, height=320, title=None):
    """Apply the shared off-white/burgundy theme to any Plotly figure, with a smooth transition on data updates."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=CHART_PAPER,
        plot_bgcolor=CHART_BG,
        font=CHART_FONT,
        height=height,
        title=dict(text=title, font=dict(family="Libre Caslon Text, serif", color="#241414", size=16)) if title else None,
        margin=dict(t=48 if title else 20, l=10, r=10, b=10),
        legend=dict(bgcolor="rgba(255,255,255,0.6)", bordercolor=CHART_GRID, borderwidth=1, font=dict(color="#241414")),
        transition=dict(duration=400, easing="cubic-in-out")
    )
    fig.update_xaxes(
        gridcolor=CHART_GRID, zerolinecolor=CHART_GRID,
        tickfont=dict(color="#241414"), title_font=dict(color="#241414")
    )
    fig.update_yaxes(
        gridcolor=CHART_GRID, zerolinecolor=CHART_GRID,
        tickfont=dict(color="#241414"), title_font=dict(color="#241414")
    )
    return fig

ROLE_COLORS = {
    'Batter': '#3B5BA5',
    'Bowler': '#9B2335',
    'All-rounder': '#6E1423'
}

# ── Data loading ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    batting = pd.read_csv("batting_by_season.csv")
    bowling = pd.read_csv("bowling_by_season.csv")
    roles = pd.read_csv("player_roles.csv")
    roles.columns = ['Player', 'balls_faced', 'balls_bowled', 'role']
    batting_phase = pd.read_csv("batting_by_phase.csv")
    bowling_phase = pd.read_csv("bowling_by_phase.csv")
    batting_innings = pd.read_csv("batting_innings.csv")
    bowling_innings = pd.read_csv("bowling_innings.csv")
    wicket_types = pd.read_csv("bowler_wicket_types.csv")
    return batting, bowling, roles, batting_phase, bowling_phase, batting_innings, bowling_innings, wicket_types

try:
    batting_df, bowling_df, roles_df, batting_phase_df, bowling_phase_df, batting_innings_df, bowling_innings_df, wicket_types_df = load_data()
    DATA_LOADED = True
except FileNotFoundError:
    DATA_LOADED = False

if not DATA_LOADED:
    st.error("Data files not found. Make sure all CSV outputs are in this folder. Run `pipeline.py` then `pipeline_extended.py` first.")
    st.stop()

# Filter out insufficient-data players from selector — not auction relevant
eligible_players = roles_df[roles_df['role'] != 'Insufficient data'].copy()
eligible_players = eligible_players.sort_values('Player')

# ── SHORTLIST STATE ──────────────────────────────────────────────────────────────
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []

def add_to_shortlist(player_name):
    if player_name not in st.session_state.shortlist:
        st.session_state.shortlist.append(player_name)

def remove_from_shortlist(player_name):
    if player_name in st.session_state.shortlist:
        st.session_state.shortlist.remove(player_name)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏏 IPL AUCTION INTEL")
    st.markdown("---")

    st.markdown("**SELECT MODE**")
    mode = st.radio("View", ["Player Card", "Compare Players", "⭐ Shortlist"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**FILTER BY ROLE**")
    role_filter = st.multiselect(
        "Role",
        options=['Batter', 'Bowler', 'All-rounder'],
        default=['Batter', 'Bowler', 'All-rounder'],
        label_visibility="collapsed"
    )

    filtered_players = eligible_players[eligible_players['role'].isin(role_filter)]
    player_list = filtered_players['Player'].tolist()

    st.markdown("---")

    if mode == "Player Card":
        st.markdown("**SELECT PLAYER**")
        selected_player = st.selectbox("Player", options=player_list, label_visibility="collapsed")
    else:
        st.markdown("**SELECT PLAYERS (2-4)**")
        selected_players_compare = st.multiselect(
            "Players", options=player_list, default=player_list[:2] if len(player_list) >= 2 else player_list,
            label_visibility="collapsed", max_selections=4
        )

    st.markdown("---")
    st.markdown("**RECENT FORM WINDOW**")
    recent_n = st.slider("Last N seasons", min_value=1, max_value=5, value=3, label_visibility="collapsed")

    st.markdown("---")
    st.caption("DATA: Cricsheet (via GitHub mirror) · 2008–2026 · 295K+ deliveries")

    st.markdown("---")
    n_shortlisted = len(st.session_state.shortlist)
    st.markdown(f"⭐ **Shortlist: {n_shortlisted} player{'s' if n_shortlisted != 1 else ''}**")


# ── Helper functions ─────────────────────────────────────────────────────────
def get_player_role(player_name):
    row = roles_df[roles_df['Player'] == player_name]
    if row.empty:
        return "Unknown"
    return row.iloc[0]['role']

def get_batting_stats(player_name):
    return batting_df[batting_df['Batter'] == player_name].sort_values('season')

def get_bowling_stats(player_name):
    return bowling_df[bowling_df['Bowler'] == player_name].sort_values('season')

def career_batting_summary(bat_data):
    if bat_data.empty:
        return None
    total_runs = bat_data['runs'].sum()
    total_balls = bat_data['balls_faced'].sum()
    total_dismissals = bat_data['dismissals'].sum()
    total_fours = int(bat_data['fours'].sum())
    total_sixes = int(bat_data['sixes'].sum())
    sr = round(total_runs / total_balls * 100, 2) if total_balls > 0 else 0
    avg = round(total_runs / total_dismissals, 2) if total_dismissals > 0 else np.nan
    boundary_pct = round((total_fours + total_sixes) / total_balls * 100, 2) if total_balls > 0 else 0
    return {
        'runs': int(total_runs), 'balls': int(total_balls),
        'strike_rate': sr, 'average': avg,
        'seasons': bat_data['season'].nunique(),
        'fours': total_fours, 'sixes': total_sixes,
        'boundary_pct': boundary_pct
    }

def career_bowling_summary(bowl_data):
    if bowl_data.empty:
        return None
    total_runs = bowl_data['runs_conceded'].sum()
    total_overs = bowl_data['overs'].sum()
    total_wickets = bowl_data['wickets'].sum()
    economy = round(total_runs / total_overs, 2) if total_overs > 0 else 0
    avg = round(total_runs / total_wickets, 2) if total_wickets > 0 else np.nan
    return {
        'wickets': int(total_wickets), 'overs': round(total_overs, 1),
        'economy': economy, 'average': avg,
        'seasons': bowl_data['season'].nunique()
    }

def recent_vs_career(data, n_seasons):
    if data.empty:
        return None, None
    all_seasons = sorted(data['season'].unique())
    recent_seasons = all_seasons[-n_seasons:] if len(all_seasons) >= n_seasons else all_seasons
    recent_data = data[data['season'].isin(recent_seasons)]
    return data, recent_data


def consistency_badge(cv, kind='batting'):
    """Turn a coefficient-of-variation number into a coach-readable badge: (label, color)."""
    if cv is None:
        return None, None
    if kind == 'batting':
        if cv < 60:
            return "Reliable", GREEN
        elif cv < 90:
            return "Up & Down", GOLD
        else:
            return "Boom-or-Bust", RED
    else:  # bowling — economy variance, lower thresholds since economy swings less than runs
        if cv < 25:
            return "Tight & Reliable", GREEN
        elif cv < 40:
            return "Some Variance", GOLD
        else:
            return "Erratic", RED


def phase_strength_tag(phase_career_df):
    """Identify a player's strongest batting phase by strike rate, for a quick role tag."""
    if phase_career_df is None or phase_career_df.empty:
        return None
    valid = phase_career_df.dropna(subset=['strike_rate'])
    if valid.empty:
        return None
    best = valid.loc[valid['strike_rate'].idxmax()]
    tag_map = {
        'Powerplay': 'Powerplay Hitter',
        'Middle': 'Middle-Overs Anchor',
        'Death': 'Death-Overs Finisher'
    }
    return tag_map.get(best['Phase'])


def phase_economy_tag(phase_career_df):
    """Identify a bowler's strongest phase by economy (lowest = best), for a quick role tag."""
    if phase_career_df is None or phase_career_df.empty:
        return None
    valid = phase_career_df.dropna(subset=['economy'])
    if valid.empty:
        return None
    best = valid.loc[valid['economy'].idxmin()]
    tag_map = {
        'Powerplay': 'New-Ball Specialist',
        'Middle': 'Middle-Overs Controller',
        'Death': 'Death-Overs Specialist'
    }
    return tag_map.get(best['Phase'])


def generate_scouting_summary(player_name, role, bat_sum, bowl_sum, bat_phase_career, bowl_phase_career,
                                bat_cv, bowl_cv, recent_sr=None, recent_econ=None):
    """
    Build a single, coach-readable sentence describing this player's profile.
    Pulls from the same numbers already shown on the card — this is a translation
    layer, not a separate analysis — so it should never contradict the stats above it.
    """
    parts = []

    if role in ['Batter', 'All-rounder'] and bat_sum:
        bat_tag = phase_strength_tag(bat_phase_career)
        bat_label, _ = consistency_badge(bat_cv, 'batting')
        fragment = ""
        if bat_tag:
            fragment += bat_tag
        if bat_label:
            fragment += f" ({bat_label.lower()} with the bat)" if fragment else f"{bat_label} with the bat"
        if recent_sr is not None and bat_sum.get('strike_rate') is not None:
            delta = recent_sr - bat_sum['strike_rate']
            if abs(delta) >= 8:
                trend = "trending up in recent seasons" if delta > 0 else "cooling off recently"
                fragment += f", {trend}"
        if fragment:
            parts.append(fragment)

    if role in ['Bowler', 'All-rounder'] and bowl_sum:
        bowl_tag = phase_economy_tag(bowl_phase_career)
        bowl_label, _ = consistency_badge(bowl_cv, 'bowling')
        fragment = ""
        if bowl_tag:
            fragment += bowl_tag
        if bowl_label:
            fragment += f" ({bowl_label.lower()} with the ball)" if fragment else f"{bowl_label} with the ball"
        if recent_econ is not None and bowl_sum.get('economy') is not None:
            delta = recent_econ - bowl_sum['economy']
            if abs(delta) >= 1:
                trend = "leaking more runs lately" if delta > 0 else "tightening up recently"
                fragment += f", {trend}"
        if fragment:
            parts.append(fragment)

    if not parts:
        return f"{player_name} — not enough data yet for a reliable read."

    return f"{player_name}: " + "; ".join(parts) + "."


# ════════════════════════════════════════════════════════════════════════════
# MAIN — PLAYER CARD MODE
# ════════════════════════════════════════════════════════════════════════════
st.title("🏏 IPL Player Auction Analytics")

if mode == "Player Card":

    role = get_player_role(selected_player)
    role_color = ROLE_COLORS.get(role, '#888888')

    # ── Header ──────────────────────────────────────────────────────────────
    col_title, col_badge, col_action = st.columns([3, 1, 1.3])
    with col_title:
        st.markdown(f"### {selected_player}")
    with col_badge:
        st.markdown(
            f"<div class='role-badge' style='background-color:{role_color}22; color:{role_color}; border:1px solid {role_color}; text-align:center; margin-top:8px;'>{role}</div>",
            unsafe_allow_html=True
        )
    with col_action:
        already_in = selected_player in st.session_state.shortlist
        if already_in:
            st.button("✓ Shortlisted", key=f"shortlist_btn_{selected_player}", disabled=True, use_container_width=True)
        else:
            if st.button("⭐ Add to Shortlist", key=f"shortlist_btn_{selected_player}", use_container_width=True):
                add_to_shortlist(selected_player)
                st.rerun()

    st.markdown("---")

    bat_data = get_batting_stats(selected_player)
    bowl_data = get_bowling_stats(selected_player)

    bat_summary = career_batting_summary(bat_data)
    bowl_summary = career_bowling_summary(bowl_data)

    # ── SCOUTING SUMMARY — coach-readable translation of the stats below ──────
    bat_phase_career_for_summary = batting_phase_df[
        (batting_phase_df['Batter'] == selected_player) & (batting_phase_df['season'] == 'Career')
    ]
    bowl_phase_career_for_summary = bowling_phase_df[
        (bowling_phase_df['Bowler'] == selected_player) & (bowling_phase_df['season'] == 'Career')
    ]

    bat_innings_for_summary = batting_innings_df[batting_innings_df['Batter'] == selected_player]
    bowl_innings_for_summary = bowling_innings_df[bowling_innings_df['Bowler'] == selected_player]

    summary_bat_cv = None
    if len(bat_innings_for_summary) >= 3:
        m, s = bat_innings_for_summary['runs'].mean(), bat_innings_for_summary['runs'].std()
        summary_bat_cv = round((s / m) * 100, 1) if m > 0 else None

    summary_bowl_cv = None
    if len(bowl_innings_for_summary) >= 3:
        m, s = bowl_innings_for_summary['economy'].mean(), bowl_innings_for_summary['economy'].std()
        summary_bowl_cv = round((s / m) * 100, 1) if m > 0 else None

    _, recent_bat_for_summary = recent_vs_career(bat_data, recent_n) if not bat_data.empty else (None, None)
    _, recent_bowl_for_summary = recent_vs_career(bowl_data, recent_n) if not bowl_data.empty else (None, None)
    summary_recent_sr = round((recent_bat_for_summary['runs'].sum() / recent_bat_for_summary['balls_faced'].sum()) * 100, 2) \
        if recent_bat_for_summary is not None and not recent_bat_for_summary.empty and recent_bat_for_summary['balls_faced'].sum() > 0 else None
    summary_recent_econ = round(recent_bowl_for_summary['runs_conceded'].sum() / recent_bowl_for_summary['overs'].sum(), 2) \
        if recent_bowl_for_summary is not None and not recent_bowl_for_summary.empty and recent_bowl_for_summary['overs'].sum() > 0 else None

    scouting_sentence = generate_scouting_summary(
        selected_player, role, bat_summary, bowl_summary,
        bat_phase_career_for_summary, bowl_phase_career_for_summary,
        summary_bat_cv, summary_bowl_cv, summary_recent_sr, summary_recent_econ
    )

    # Tag row — quick-scan badges for a coach skimming multiple players
    tag_items = []
    if role in ['Batter', 'All-rounder'] and bat_summary:
        bt = phase_strength_tag(bat_phase_career_for_summary)
        if bt:
            tag_items.append((bt, BURGUNDY))
        bl, bc = consistency_badge(summary_bat_cv, 'batting')
        if bl:
            tag_items.append((bl, bc))
    if role in ['Bowler', 'All-rounder'] and bowl_summary:
        bwt = phase_economy_tag(bowl_phase_career_for_summary)
        if bwt:
            tag_items.append((bwt, BURGUNDY))
        bwl, bwc = consistency_badge(summary_bowl_cv, 'bowling')
        if bwl:
            tag_items.append((bwl, bwc))

    st.markdown(
        f"<div style='background:var(--card); border-left:3px solid var(--burgundy); padding:12px 16px; "
        f"border-radius:4px; margin-bottom:10px;'>"
        f"<span style='font-size:0.95rem;'>🧭 {scouting_sentence}</span></div>",
        unsafe_allow_html=True
    )

    if tag_items:
        tags_html = "".join(
            f"<span class='role-badge' style='background-color:{color}22; color:{color}; "
            f"border:1px solid {color}; margin-right:6px;'>{label}</span>"
            for label, color in tag_items
        )
        st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── BATTING SECTION ──────────────────────────────────────────────────────
    if role in ['Batter', 'All-rounder'] and bat_summary:
        st.subheader("🏏 Batting Profile")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Career Runs", f"{bat_summary['runs']:,}")
        c2.metric("Strike Rate", bat_summary['strike_rate'])
        c3.metric("Average", bat_summary['average'] if not pd.isna(bat_summary['average']) else "N/A")
        c4.metric("Seasons Played", bat_summary['seasons'])
        c5.metric("4s / 6s", f"{bat_summary['fours']} / {bat_summary['sixes']}")

        # Recent form
        all_bat, recent_bat = recent_vs_career(bat_data, recent_n)
        if recent_bat is not None and not recent_bat.empty:
            recent_sr = round((recent_bat['runs'].sum() / recent_bat['balls_faced'].sum()) * 100, 2)
            recent_runs = int(recent_bat['runs'].sum())
            delta_sr = round(recent_sr - bat_summary['strike_rate'], 2)

            st.markdown(f"**Recent Form (Last {recent_n} seasons):** {recent_runs:,} runs at {recent_sr} SR "
                        f"({'▲' if delta_sr >= 0 else '▼'} {abs(delta_sr)} vs career)")

        # Strike rate trend chart
        fig_bat = go.Figure()
        fig_bat.add_trace(go.Scatter(
            x=bat_data['season'], y=bat_data['strike_rate'],
            mode='lines+markers', name='Strike Rate',
            line=dict(color=BURGUNDY, width=3),
            marker=dict(size=8, color=BURGUNDY)
        ))
        fig_bat.update_xaxes(title='Season', dtick=1)
        fig_bat.update_yaxes(title='Strike Rate')
        style_fig(fig_bat, height=320, title="Strike Rate by Season")
        st.plotly_chart(fig_bat, use_container_width=True)

        rcol1, rcol2 = st.columns([3, 2])
        with rcol1:
            # Runs by season bar
            fig_runs = px.bar(
                bat_data, x='season', y='runs',
                labels={'runs': 'Runs', 'season': 'Season'},
                color_discrete_sequence=[GREEN]
            )
            fig_runs.update_xaxes(dtick=1)
            style_fig(fig_runs, height=300, title="Runs by Season")
            st.plotly_chart(fig_runs, use_container_width=True)

        with rcol2:
            # Scoring shape — how runs are made: dots/singles/twos vs boundaries
            total_runs = bat_data['runs'].sum()
            fours_runs = bat_data['fours'].sum() * 4
            sixes_runs = bat_data['sixes'].sum() * 6
            running_runs = max(total_runs - fours_runs - sixes_runs, 0)

            fig_shape = go.Figure(data=[go.Pie(
                labels=['Running (1s/2s/3s)', 'Fours', 'Sixes'],
                values=[running_runs, fours_runs, sixes_runs],
                hole=0.55,
                marker=dict(colors=[MUTED, GOLD, RED]),
                textinfo='percent', textfont=dict(color='#fff', size=12)
            )])
            style_fig(fig_shape, height=300, title="Scoring Shape (Career)")
            fig_shape.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.15))
            st.plotly_chart(fig_shape, use_container_width=True)

        with st.expander("📋 Full Batting Record by Season"):
            st.dataframe(
                bat_data[['season', 'runs', 'balls_faced', 'strike_rate', 'average', 'fours', 'sixes', 'dismissals']]
                .rename(columns={'season': 'Season', 'runs': 'Runs', 'balls_faced': 'Balls', 'strike_rate': 'SR',
                                  'average': 'Avg', 'fours': '4s', 'sixes': '6s', 'dismissals': 'Outs'}),
                use_container_width=True, hide_index=True
            )

        # ── PHASE SPLITS (career + per-season) ────────────────────────────────
        st.markdown("##### Strike Rate by Match Phase")

        bat_phase_career = batting_phase_df[
            (batting_phase_df['Batter'] == selected_player) & (batting_phase_df['season'] == 'Career')
        ]

        if not bat_phase_career.empty:
            phase_order = ['Powerplay', 'Middle', 'Death']
            bat_phase_career = bat_phase_career.set_index('Phase').reindex(phase_order).reset_index()

            mcol, picol = st.columns([3, 2])
            with mcol:
                pc1, pc2, pc3 = st.columns(3)
                phase_cols = {'Powerplay': pc1, 'Middle': pc2, 'Death': pc3}
                phase_icons = {'Powerplay': '🚀', 'Middle': '⚙️', 'Death': '🔥'}
                for _, prow in bat_phase_career.iterrows():
                    if pd.notna(prow['Phase']):
                        with phase_cols[prow['Phase']]:
                            st.metric(
                                f"{phase_icons[prow['Phase']]} {prow['Phase']} SR",
                                prow['strike_rate'] if pd.notna(prow['strike_rate']) else "N/A",
                                help=f"{int(prow['runs'])} runs off {int(prow['balls_faced'])} balls"
                            )
                            st.caption(
                                f"🏏 {int(prow['runs'])} runs · 4️⃣ {int(prow['fours'])} · 6️⃣ {int(prow['sixes'])} "
                                f"· Boundary%: {prow['boundary_pct']}%"
                            )
            with picol:
                # Where their runs actually come from — phase share of career runs
                phase_labels_list = bat_phase_career['Phase'].tolist()
                fig_phase_pie = go.Figure(data=[go.Pie(
                    labels=phase_labels_list,
                    values=bat_phase_career['runs'],
                    customdata=phase_labels_list,  # guaranteed to come back in the click event,
                    hole=0.55,                      # unlike 'label'/'legendgroup' which aren't reliable for pies
                    marker=dict(colors=['#3B5BA5', GOLD, RED]),
                    textinfo='percent', textfont=dict(color='#fff', size=12)
                )])
                style_fig(fig_phase_pie, height=270, title="Run Share by Phase — click a slice to filter ↓")
                fig_phase_pie.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.15))
                pie_event = st.plotly_chart(
                    fig_phase_pie, use_container_width=True,
                    on_select="rerun", selection_mode="points",
                    key=f"phase_pie_{selected_player}"
                )

            # Read back which slice (if any) was clicked.
            clicked_phase = None
            if pie_event and pie_event.get("selection", {}).get("points"):
                pt = pie_event["selection"]["points"][0]
                cd = pt.get("customdata")
                if cd:
                    # customdata comes back as a list (it's set per-point as a scalar here, but
                    # Plotly always wraps point-level customdata in a list), so unwrap it.
                    clicked_phase = cd[0] if isinstance(cd, list) else cd
                else:
                    # Fallback for older Plotly/Streamlit combos that do expose label/legendgroup
                    clicked_phase = pt.get("label") or pt.get("legendgroup")

            with st.expander("🔧 Debug: raw click event (temporary — remove once confirmed working)"):
                st.write(pie_event)

            if clicked_phase:
                fcol1, fcol2 = st.columns([5, 1])
                with fcol1:
                    st.caption(f"🔎 Filtered to **{clicked_phase}** — click the same slice again, or press Clear, to reset.")
                with fcol2:
                    if st.button("Clear", key=f"clear_phase_{selected_player}"):
                        st.rerun()

            # Per-season phase trend chart
            bat_phase_season = batting_phase_df[
                (batting_phase_df['Batter'] == selected_player) & (batting_phase_df['season'] != 'Career')
            ].copy()
            bat_phase_season['season'] = bat_phase_season['season'].astype(int)

            if clicked_phase:
                bat_phase_season = bat_phase_season[bat_phase_season['Phase'] == clicked_phase]

            if not bat_phase_season.empty:
                chart_title = f"Strike Rate by Season — {clicked_phase}" if clicked_phase else "Phase-wise Strike Rate by Season"
                fig_phase = px.line(
                    bat_phase_season.sort_values('season'), x='season', y='strike_rate', color='Phase',
                    markers=True,
                    color_discrete_map={'Powerplay': '#3B5BA5', 'Middle': GOLD, 'Death': RED},
                    labels={'strike_rate': 'Strike Rate', 'season': 'Season'}
                )
                fig_phase.update_xaxes(dtick=1)
                style_fig(fig_phase, height=320, title=chart_title)
                st.plotly_chart(fig_phase, use_container_width=True)
        else:
            st.caption("No phase-level data available for this player.")

        # ── CONSISTENCY — innings-level spread ────────────────────────────────
        st.markdown("##### Consistency — Innings-by-Innings Spread")

        player_innings_bat = batting_innings_df[batting_innings_df['Batter'] == selected_player]

        if not player_innings_bat.empty and len(player_innings_bat) >= 3:
            std_runs = round(player_innings_bat['runs'].std(), 2)
            mean_runs = round(player_innings_bat['runs'].mean(), 2)
            cv = round((std_runs / mean_runs) * 100, 1) if mean_runs > 0 else None
            badge_label, badge_color = consistency_badge(cv, 'batting')

            if badge_label:
                coach_lines = {
                    "Reliable": f"Scores around {int(mean_runs)} most innings — a dependable, low-risk pick.",
                    "Up & Down": f"Averages {int(mean_runs)}, but swings between quiet games and big scores.",
                    "Boom-or-Bust": f"Capable of match-winning innings, but just as likely to fail — high risk, high reward."
                }
                st.markdown(
                    f"<span class='role-badge' style='background-color:{badge_color}22; color:{badge_color}; "
                    f"border:1px solid {badge_color};'>{badge_label}</span> "
                    f"<span style='color:var(--muted); font-size:0.9rem;'>{coach_lines.get(badge_label, '')}</span>",
                    unsafe_allow_html=True
                )

            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Innings Played", len(player_innings_bat))
            cc2.metric("Avg Runs / Innings", mean_runs)
            cc3.metric("Std Dev (Runs)", std_runs,
                       help="Lower = more consistent. Higher = boom-or-bust.")

            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                y=player_innings_bat['runs'], name=selected_player,
                marker_color=BURGUNDY, line=dict(color=BURGUNDY), boxmean='sd'
            ))
            fig_box.update_yaxes(title='Runs per Innings')
            style_fig(fig_box, height=340, title="Distribution of Runs per Innings (career)")
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

            if cv is not None:
                st.caption(f"Coefficient of variation: {cv}% (technical detail for analysts — lower is steadier)")
        else:
            st.caption("Not enough innings to compute a reliable consistency score.")

    # ── BOWLING SECTION ──────────────────────────────────────────────────────
    if role in ['Bowler', 'All-rounder'] and bowl_summary:
        st.subheader("🎯 Bowling Profile")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Career Wickets", bowl_summary['wickets'])
        c2.metric("Economy Rate", bowl_summary['economy'])
        c3.metric("Bowling Average", bowl_summary['average'] if not pd.isna(bowl_summary['average']) else "N/A")
        c4.metric("Seasons Played", bowl_summary['seasons'])

        all_bowl, recent_bowl = recent_vs_career(bowl_data, recent_n)
        if recent_bowl is not None and not recent_bowl.empty:
            recent_econ = round(recent_bowl['runs_conceded'].sum() / recent_bowl['overs'].sum(), 2)
            recent_wkts = int(recent_bowl['wickets'].sum())
            delta_econ = round(recent_econ - bowl_summary['economy'], 2)

            st.markdown(f"**Recent Form (Last {recent_n} seasons):** {recent_wkts} wickets at {recent_econ} economy "
                        f"({'▲' if delta_econ >= 0 else '▼'} {abs(delta_econ)} vs career — "
                        f"{'worse' if delta_econ >= 0 else 'better'})")

        fig_econ = go.Figure()
        fig_econ.add_trace(go.Scatter(
            x=bowl_data['season'], y=bowl_data['economy'],
            mode='lines+markers', name='Economy',
            line=dict(color=RED, width=3),
            marker=dict(size=8, color=RED)
        ))
        fig_econ.update_xaxes(title='Season', dtick=1)
        fig_econ.update_yaxes(title='Economy Rate')
        style_fig(fig_econ, height=320, title="Economy Rate by Season")
        st.plotly_chart(fig_econ, use_container_width=True)

        wcol1, wcol2 = st.columns([3, 2])
        with wcol1:
            fig_wkts = px.bar(
                bowl_data, x='season', y='wickets',
                labels={'wickets': 'Wickets', 'season': 'Season'},
                color_discrete_sequence=[GREEN]
            )
            fig_wkts.update_xaxes(dtick=1)
            style_fig(fig_wkts, height=300, title="Wickets by Season")
            st.plotly_chart(fig_wkts, use_container_width=True)

        with wcol2:
            # How they get their wickets — dismissal type breakdown
            player_wicket_types = wicket_types_df[wicket_types_df['Bowler'] == selected_player]
            if not player_wicket_types.empty:
                fig_wtype_pie = go.Figure(data=[go.Pie(
                    labels=player_wicket_types['Kind'].str.title(),
                    values=player_wicket_types['count'],
                    hole=0.55,
                    marker=dict(colors=PLAYER_PALETTE),
                    textinfo='percent', textfont=dict(color='#fff', size=11)
                )])
                style_fig(fig_wtype_pie, height=300, title="Wicket Types (Career)")
                fig_wtype_pie.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.2, font=dict(size=9)))
                st.plotly_chart(fig_wtype_pie, use_container_width=True)
            else:
                st.caption("No wicket-type data available.")

        with st.expander("📋 Full Bowling Record by Season"):
            st.dataframe(
                bowl_data[['season', 'overs', 'runs_conceded', 'wickets', 'economy', 'bowling_avg']]
                .rename(columns={'season': 'Season', 'overs': 'Overs', 'runs_conceded': 'Runs Conceded',
                                  'wickets': 'Wickets', 'economy': 'Economy', 'bowling_avg': 'Average'}),
                use_container_width=True, hide_index=True
            )

        # ── PHASE SPLITS (career + per-season) ────────────────────────────────
        st.markdown("##### Economy by Match Phase")

        bowl_phase_career = bowling_phase_df[
            (bowling_phase_df['Bowler'] == selected_player) & (bowling_phase_df['season'] == 'Career')
        ]

        if not bowl_phase_career.empty:
            phase_order = ['Powerplay', 'Middle', 'Death']
            bowl_phase_career = bowl_phase_career.set_index('Phase').reindex(phase_order).reset_index()

            bmcol, bpicol = st.columns([3, 2])
            with bmcol:
                pc1, pc2, pc3 = st.columns(3)
                phase_cols = {'Powerplay': pc1, 'Middle': pc2, 'Death': pc3}
                phase_icons = {'Powerplay': '🚀', 'Middle': '⚙️', 'Death': '🔥'}
                for _, prow in bowl_phase_career.iterrows():
                    if pd.notna(prow['Phase']):
                        with phase_cols[prow['Phase']]:
                            st.metric(
                                f"{phase_icons[prow['Phase']]} {prow['Phase']} Econ",
                                prow['economy'] if pd.notna(prow['economy']) else "N/A",
                                help=f"{int(prow['runs_conceded'])} runs off {prow['overs']:.1f} overs"
                            )
            with bpicol:
                # Where overs are bowled — phase share of total overs bowled
                fig_overs_pie = go.Figure(data=[go.Pie(
                    labels=bowl_phase_career['Phase'],
                    values=bowl_phase_career['overs'],
                    hole=0.55,
                    marker=dict(colors=['#3B5BA5', GOLD, RED]),
                    textinfo='percent', textfont=dict(color='#fff', size=12)
                )])
                style_fig(fig_overs_pie, height=270, title="Overs Bowled by Phase")
                fig_overs_pie.update_layout(showlegend=True, legend=dict(orientation='h', y=-0.15))
                st.plotly_chart(fig_overs_pie, use_container_width=True)

            bowl_phase_season = bowling_phase_df[
                (bowling_phase_df['Bowler'] == selected_player) & (bowling_phase_df['season'] != 'Career')
            ].copy()
            bowl_phase_season['season'] = bowl_phase_season['season'].astype(int)

            if not bowl_phase_season.empty:
                fig_phase_b = px.line(
                    bowl_phase_season.sort_values('season'), x='season', y='economy', color='Phase',
                    markers=True,
                    color_discrete_map={'Powerplay': '#3B5BA5', 'Middle': GOLD, 'Death': RED},
                    labels={'economy': 'Economy', 'season': 'Season'}
                )
                fig_phase_b.update_xaxes(dtick=1)
                style_fig(fig_phase_b, height=320, title="Phase-wise Economy by Season")
                st.plotly_chart(fig_phase_b, use_container_width=True)
        else:
            st.caption("No phase-level data available for this player.")

        # ── CONSISTENCY — innings-level spread ────────────────────────────────
        st.markdown("##### Consistency — Innings-by-Innings Spread")

        player_innings_bowl = bowling_innings_df[bowling_innings_df['Bowler'] == selected_player]

        if not player_innings_bowl.empty and len(player_innings_bowl) >= 3:
            std_econ = round(player_innings_bowl['economy'].std(), 2)
            mean_econ = round(player_innings_bowl['economy'].mean(), 2)
            cv_b = round((std_econ / mean_econ) * 100, 1) if mean_econ > 0 else None
            badge_label_b, badge_color_b = consistency_badge(cv_b, 'bowling')

            if badge_label_b:
                coach_lines_b = {
                    "Tight & Reliable": f"Concedes around {mean_econ} runs per over most matches — a safe bowler to trust with the ball.",
                    "Some Variance": f"Averages {mean_econ} economy overall, but has the occasional expensive night mixed in.",
                    "Erratic": f"Economy swings wildly match to match — can be brilliant or expensive, hard to predict."
                }
                st.markdown(
                    f"<span class='role-badge' style='background-color:{badge_color_b}22; color:{badge_color_b}; "
                    f"border:1px solid {badge_color_b};'>{badge_label_b}</span> "
                    f"<span style='color:var(--muted); font-size:0.9rem;'>{coach_lines_b.get(badge_label_b, '')}</span>",
                    unsafe_allow_html=True
                )

            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Innings Bowled", len(player_innings_bowl))
            cc2.metric("Avg Economy / Innings", mean_econ)
            cc3.metric("Std Dev (Economy)", std_econ,
                       help="Lower = more consistent control. Higher = erratic.")

            fig_box_b = go.Figure()
            fig_box_b.add_trace(go.Box(
                y=player_innings_bowl['economy'], name=selected_player,
                marker_color=RED, line=dict(color=RED), boxmean='sd'
            ))
            fig_box_b.update_yaxes(title='Economy per Innings')
            style_fig(fig_box_b, height=340, title="Distribution of Economy per Innings (career)")
            fig_box_b.update_layout(showlegend=False)
            st.plotly_chart(fig_box_b, use_container_width=True)

            if cv_b is not None:
                st.caption(f"Coefficient of variation: {cv_b}% (technical detail for analysts — lower is steadier)")
        else:
            st.caption("Not enough innings to compute a reliable consistency score.")

    if not bat_summary and not bowl_summary:
        st.warning("No sufficient data available for this player.")


# ════════════════════════════════════════════════════════════════════════════
# MAIN — COMPARE PLAYERS MODE
# ════════════════════════════════════════════════════════════════════════════
elif mode == "Compare Players":
    if len(selected_players_compare) < 2:
        st.warning("Select at least 2 players from the sidebar to compare.")
        st.stop()

    st.markdown(f"### Comparing {len(selected_players_compare)} Players")
    st.markdown("---")

    # ── Build summary data for each player ──────────────────────────────────
    compare_data = []
    for p in selected_players_compare:
        role = get_player_role(p)
        bat = get_batting_stats(p)
        bowl = get_bowling_stats(p)
        bat_sum = career_batting_summary(bat)
        bowl_sum = career_bowling_summary(bowl)

        _, recent_bat = recent_vs_career(bat, recent_n) if not bat.empty else (None, None)
        _, recent_bowl = recent_vs_career(bowl, recent_n) if not bowl.empty else (None, None)

        recent_sr = round((recent_bat['runs'].sum() / recent_bat['balls_faced'].sum()) * 100, 2) \
            if recent_bat is not None and not recent_bat.empty and recent_bat['balls_faced'].sum() > 0 else None
        recent_econ = round(recent_bowl['runs_conceded'].sum() / recent_bowl['overs'].sum(), 2) \
            if recent_bowl is not None and not recent_bowl.empty and recent_bowl['overs'].sum() > 0 else None

        compare_data.append({
            'player': p, 'role': role,
            'bat_data': bat, 'bowl_data': bowl,
            'bat_summary': bat_sum, 'bowl_summary': bowl_sum,
            'recent_sr': recent_sr, 'recent_econ': recent_econ
        })

    # ── SIDE-BY-SIDE PLAYER CARDS ─────────────────────────────────────────────
    cols = st.columns(len(compare_data))
    PLAYER_COLORS = PLAYER_PALETTE

    for i, (col, pdata) in enumerate(zip(cols, compare_data)):
        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        with col:
            st.markdown(
                f"<div style='border-top:3px solid {color}; padding-top:10px;'>"
                f"<h4 style='margin-bottom:2px;'>{pdata['player']}</h4>"
                f"<span class='role-badge' style='background-color:{ROLE_COLORS.get(pdata['role'],'#888')}22; "
                f"color:{ROLE_COLORS.get(pdata['role'],'#888')}; border:1px solid {ROLE_COLORS.get(pdata['role'],'#888')};'>"
                f"{pdata['role']}</span></div>",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            if pdata['bat_summary']:
                bs = pdata['bat_summary']
                st.metric("Career Runs", f"{bs['runs']:,}")
                st.metric("Strike Rate", bs['strike_rate'])
                st.metric("Average", bs['average'] if not pd.isna(bs['average']) else "N/A")
                if pdata['recent_sr'] is not None:
                    delta = round(pdata['recent_sr'] - bs['strike_rate'], 1)
                    st.caption(f"Last {recent_n}s SR: {pdata['recent_sr']} ({'▲' if delta>=0 else '▼'}{abs(delta)})")

            if pdata['bowl_summary']:
                bws = pdata['bowl_summary']
                st.metric("Career Wickets", bws['wickets'])
                st.metric("Economy", bws['economy'])
                st.metric("Bowl Avg", bws['average'] if not pd.isna(bws['average']) else "N/A")
                if pdata['recent_econ'] is not None:
                    delta = round(pdata['recent_econ'] - bws['economy'], 1)
                    st.caption(f"Last {recent_n}s Econ: {pdata['recent_econ']} ({'▲' if delta>=0 else '▼'}{abs(delta)})")

            if not pdata['bat_summary'] and not pdata['bowl_summary']:
                st.warning("No data")

            already_in = pdata['player'] in st.session_state.shortlist
            if already_in:
                st.button("✓ Shortlisted", key=f"cmp_shortlist_{pdata['player']}", disabled=True, use_container_width=True)
            else:
                if st.button("⭐ Add", key=f"cmp_shortlist_{pdata['player']}", use_container_width=True):
                    add_to_shortlist(pdata['player'])
                    st.rerun()

    st.markdown("---")

    # ── COMPARISON CHARTS ──────────────────────────────────────────────────────
    has_batters = any(p['bat_summary'] for p in compare_data)
    has_bowlers = any(p['bowl_summary'] for p in compare_data)

    if has_batters:
        st.subheader("🏏 Strike Rate Trend — Batting")
        fig_cmp_bat = go.Figure()
        for i, pdata in enumerate(compare_data):
            if not pdata['bat_data'].empty:
                color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
                fig_cmp_bat.add_trace(go.Scatter(
                    x=pdata['bat_data']['season'], y=pdata['bat_data']['strike_rate'],
                    mode='lines+markers', name=pdata['player'],
                    line=dict(color=color, width=3), marker=dict(size=7)
                ))
        fig_cmp_bat.update_xaxes(title='Season', dtick=1)
        fig_cmp_bat.update_yaxes(title='Strike Rate')
        style_fig(fig_cmp_bat, height=380)
        st.plotly_chart(fig_cmp_bat, use_container_width=True)

        # Grouped bar — career batting metrics side by side
        bat_compare_rows = []
        for pdata in compare_data:
            if pdata['bat_summary']:
                bat_compare_rows.append({
                    'Player': pdata['player'],
                    'Runs': pdata['bat_summary']['runs'],
                    'Strike Rate': pdata['bat_summary']['strike_rate'],
                    'Average': pdata['bat_summary']['average'] if not pd.isna(pdata['bat_summary']['average']) else 0
                })
        if bat_compare_rows:
            bat_cmp_df = pd.DataFrame(bat_compare_rows)
            fig_bat_bars = px.bar(
                bat_cmp_df, x='Player', y='Strike Rate', color='Player',
                color_discrete_sequence=PLAYER_COLORS,
                text='Strike Rate'
            )
            fig_bat_bars.update_traces(textposition='outside')
            style_fig(fig_bat_bars, height=320, title="Career Strike Rate Comparison")
            fig_bat_bars.update_layout(showlegend=False)
            st.plotly_chart(fig_bat_bars, use_container_width=True)

        # ── PHASE-WISE COMPARISON: runs, 4s, 6s per phase across selected players ──
        st.markdown("##### Phase-wise Output Comparison")
        phase_choice = st.radio(
            "Compare by phase:", ["Powerplay", "Middle", "Death"],
            horizontal=True, key="phase_compare_radio"
        )

        phase_rows = []
        for pdata in compare_data:
            if pdata['bat_summary']:
                prow = batting_phase_df[
                    (batting_phase_df['Batter'] == pdata['player']) &
                    (batting_phase_df['season'] == 'Career') &
                    (batting_phase_df['Phase'] == phase_choice)
                ]
                if not prow.empty:
                    r = prow.iloc[0]
                    phase_rows.append({
                        'Player': pdata['player'], 'Runs': int(r['runs']),
                        'Fours': int(r['fours']), 'Sixes': int(r['sixes']),
                        'Strike Rate': r['strike_rate'], 'Balls Faced': int(r['balls_faced'])
                    })

        if phase_rows:
            phase_cmp_df = pd.DataFrame(phase_rows)

            pcol1, pcol2 = st.columns(2)
            with pcol1:
                fig_runs_cmp = px.bar(
                    phase_cmp_df, x='Player', y='Runs', color='Player',
                    color_discrete_sequence=PLAYER_COLORS, text='Runs'
                )
                fig_runs_cmp.update_traces(textposition='outside')
                style_fig(fig_runs_cmp, height=300, title=f"Runs in {phase_choice}")
                fig_runs_cmp.update_layout(showlegend=False)
                st.plotly_chart(fig_runs_cmp, use_container_width=True)

            with pcol2:
                fig_sixes_cmp = go.Figure()
                fig_sixes_cmp.add_trace(go.Bar(
                    x=phase_cmp_df['Player'], y=phase_cmp_df['Fours'], name='4s',
                    marker_color='#3B5BA5', text=phase_cmp_df['Fours'], textposition='outside'
                ))
                fig_sixes_cmp.add_trace(go.Bar(
                    x=phase_cmp_df['Player'], y=phase_cmp_df['Sixes'], name='6s',
                    marker_color=GOLD, text=phase_cmp_df['Sixes'], textposition='outside'
                ))
                fig_sixes_cmp.update_layout(barmode='group')
                style_fig(fig_sixes_cmp, height=300, title=f"Boundaries in {phase_choice}")
                st.plotly_chart(fig_sixes_cmp, use_container_width=True)

            st.dataframe(phase_cmp_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No phase data available for selected players.")
        st.subheader("🎯 Economy Trend — Bowling")
        fig_cmp_bowl = go.Figure()
        for i, pdata in enumerate(compare_data):
            if not pdata['bowl_data'].empty:
                color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
                fig_cmp_bowl.add_trace(go.Scatter(
                    x=pdata['bowl_data']['season'], y=pdata['bowl_data']['economy'],
                    mode='lines+markers', name=pdata['player'],
                    line=dict(color=color, width=3), marker=dict(size=7)
                ))
        fig_cmp_bowl.update_xaxes(title='Season', dtick=1)
        fig_cmp_bowl.update_yaxes(title='Economy Rate')
        style_fig(fig_cmp_bowl, height=380)
        st.plotly_chart(fig_cmp_bowl, use_container_width=True)

        bowl_compare_rows = []
        for pdata in compare_data:
            if pdata['bowl_summary']:
                bowl_compare_rows.append({
                    'Player': pdata['player'],
                    'Wickets': pdata['bowl_summary']['wickets'],
                    'Economy': pdata['bowl_summary']['economy'],
                })
        if bowl_compare_rows:
            bowl_cmp_df = pd.DataFrame(bowl_compare_rows)
            fig_bowl_bars = px.bar(
                bowl_cmp_df, x='Player', y='Wickets', color='Player',
                color_discrete_sequence=PLAYER_COLORS,
                text='Wickets'
            )
            fig_bowl_bars.update_traces(textposition='outside')
            style_fig(fig_bowl_bars, height=320, title="Career Wickets Comparison")
            fig_bowl_bars.update_layout(showlegend=False)
            st.plotly_chart(fig_bowl_bars, use_container_width=True)

    # ── FULL COMPARISON TABLE ──────────────────────────────────────────────────
    with st.expander("📋 Full Side-by-Side Summary Table"):
        summary_rows = []
        for pdata in compare_data:
            row = {'Player': pdata['player'], 'Role': pdata['role']}
            if pdata['bat_summary']:
                bs = pdata['bat_summary']
                row.update({'Runs': bs['runs'], 'Bat SR': bs['strike_rate'],
                            'Bat Avg': bs['average'], '4s': bs['fours'], '6s': bs['sixes']})
            if pdata['bowl_summary']:
                bws = pdata['bowl_summary']
                row.update({'Wickets': bws['wickets'], 'Economy': bws['economy'], 'Bowl Avg': bws['average']})
            summary_rows.append(row)
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# MAIN — SHORTLIST MODE
# ════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("### ⭐ Auction Shortlist")
    st.caption("Players you've flagged as potential auction targets. Add players from the Player Card or Compare views.")
    st.markdown("---")

    shortlist = st.session_state.shortlist

    if not shortlist:
        st.info("Your shortlist is empty. Go to **Player Card** or **Compare Players** and click **⭐ Add to Shortlist** on anyone you want to track here.")
        st.stop()

    # ── Build summary rows for everyone on the shortlist ──────────────────────
    shortlist_rows = []
    shortlist_raw = {}

    for p in shortlist:
        role = get_player_role(p)
        bat = get_batting_stats(p)
        bowl = get_bowling_stats(p)
        bat_sum = career_batting_summary(bat)
        bowl_sum = career_bowling_summary(bowl)

        _, recent_bat = recent_vs_career(bat, recent_n) if not bat.empty else (None, None)
        _, recent_bowl = recent_vs_career(bowl, recent_n) if not bowl.empty else (None, None)
        recent_sr = round((recent_bat['runs'].sum() / recent_bat['balls_faced'].sum()) * 100, 2) \
            if recent_bat is not None and not recent_bat.empty and recent_bat['balls_faced'].sum() > 0 else None
        recent_econ = round(recent_bowl['runs_conceded'].sum() / recent_bowl['overs'].sum(), 2) \
            if recent_bowl is not None and not recent_bowl.empty and recent_bowl['overs'].sum() > 0 else None

        # Consistency label
        innings_bat = batting_innings_df[batting_innings_df['Batter'] == p]
        innings_bowl = bowling_innings_df[bowling_innings_df['Bowler'] == p]
        cv_bat = None
        if len(innings_bat) >= 3:
            m, s = innings_bat['runs'].mean(), innings_bat['runs'].std()
            cv_bat = round((s / m) * 100, 1) if m > 0 else None

        row = {'Player': p, 'Role': role}
        # Role-gate stats — a bowler's incidental batting stats (or vice versa)
        # shouldn't appear, or they'll distort the radar/table with irrelevant numbers
        if role in ['Batter', 'All-rounder'] and bat_sum:
            row.update({
                'Runs': bat_sum['runs'], 'Bat SR': bat_sum['strike_rate'],
                'Bat Avg': bat_sum['average'], 'Recent SR': recent_sr,
                '4s': bat_sum['fours'], '6s': bat_sum['sixes'],
                'Boundary %': bat_sum['boundary_pct']
            })
        if role in ['Bowler', 'All-rounder'] and bowl_sum:
            row.update({
                'Wickets': bowl_sum['wickets'], 'Economy': bowl_sum['economy'],
                'Bowl Avg': bowl_sum['average'], 'Recent Econ': recent_econ
            })
        if cv_bat is not None and role in ['Batter', 'All-rounder']:
            row['Consistency (CV%)'] = cv_bat

        shortlist_rows.append(row)
        shortlist_raw[p] = {'role': role, 'bat_sum': bat_sum, 'bowl_sum': bowl_sum}

    shortlist_df = pd.DataFrame(shortlist_rows)

    # ── Summary table with remove buttons ──────────────────────────────────────
    st.markdown(f"**{len(shortlist)} player(s) shortlisted**")

    for p in shortlist:
        rcol1, rcol2 = st.columns([6, 1])
        with rcol1:
            r = shortlist_raw[p]
            badge_color = ROLE_COLORS.get(r['role'], '#888')
            line = f"**{p}** "
            if r['role'] in ['Batter', 'All-rounder'] and r['bat_sum']:
                line += f"· {r['bat_sum']['runs']:,} runs, SR {r['bat_sum']['strike_rate']} "
            if r['role'] in ['Bowler', 'All-rounder'] and r['bowl_sum']:
                line += f"· {r['bowl_sum']['wickets']} wkts, Econ {r['bowl_sum']['economy']} "
            st.markdown(
                f"<span class='role-badge' style='background-color:{badge_color}22; color:{badge_color}; "
                f"border:1px solid {badge_color}; margin-right:8px;'>{r['role']}</span> {line}",
                unsafe_allow_html=True
            )
        with rcol2:
            if st.button("✕ Remove", key=f"remove_{p}"):
                remove_from_shortlist(p)
                st.rerun()

    st.markdown("---")

    tcol, picol = st.columns([3, 2])
    with tcol:
        st.dataframe(shortlist_df, use_container_width=True, hide_index=True)
    with picol:
        # Squad balance check — role mix of shortlisted players
        role_counts = shortlist_df['Role'].value_counts()
        fig_role_pie = go.Figure(data=[go.Pie(
            labels=role_counts.index, values=role_counts.values,
            hole=0.55,
            marker=dict(colors=[ROLE_COLORS.get(r, MUTED) for r in role_counts.index]),
            textinfo='label+value', textfont=dict(color='#fff', size=11)
        )])
        style_fig(fig_role_pie, height=280, title="Squad Balance — Role Mix")
        fig_role_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_role_pie, use_container_width=True)

    st.markdown("---")

    # ── RADAR CHART — normalized comparison across shortlisted players ─────────
    st.subheader("📊 Shortlist Radar Comparison")
    st.caption("Each metric is normalized 0–100 relative to the players on this shortlist, so batting and bowling stats can sit on the same chart.")

    if len(shortlist) < 2:
        st.info("Add at least 2 players to see the radar comparison.")
    else:
        # Define normalized metric set — direction-aware (higher-is-better flips for economy/avg conceded)
        radar_metrics = []

        has_any_bat = any(shortlist_raw[p]['role'] in ['Batter', 'All-rounder'] and shortlist_raw[p]['bat_sum'] for p in shortlist)
        has_any_bowl = any(shortlist_raw[p]['role'] in ['Bowler', 'All-rounder'] and shortlist_raw[p]['bowl_sum'] for p in shortlist)

        if has_any_bat:
            radar_metrics += ['Runs', 'Bat SR', 'Bat Avg', '4s', '6s', 'Boundary %']
        if has_any_bowl:
            radar_metrics += ['Wickets', 'Economy', 'Bowl Avg']

        radar_metrics = [m for m in radar_metrics if m in shortlist_df.columns]

        if len(radar_metrics) < 3:
            st.info("Not enough overlapping metrics across shortlisted players to build a radar chart. Try shortlisting players of the same role (all batters, or all bowlers) for a cleaner comparison.")
        else:
            norm_df = shortlist_df.copy()
            LOWER_IS_BETTER = {'Economy', 'Bowl Avg'}

            for metric in radar_metrics:
                col_vals = norm_df[metric]
                if col_vals.notna().sum() < 2:
                    norm_df[metric + '_norm'] = 50  # not enough spread, neutral
                    continue
                vmin, vmax = col_vals.min(), col_vals.max()
                if vmax == vmin:
                    norm_df[metric + '_norm'] = 50
                else:
                    if metric in LOWER_IS_BETTER:
                        norm_df[metric + '_norm'] = ((vmax - col_vals) / (vmax - vmin) * 100).round(1)
                    else:
                        norm_df[metric + '_norm'] = ((col_vals - vmin) / (vmax - vmin) * 100).round(1)

            fig_radar = go.Figure()
            radar_colors = PLAYER_PALETTE

            for i, row in norm_df.iterrows():
                values = [row.get(m + '_norm', 0) for m in radar_metrics]
                values.append(values[0])  # close the loop
                labels = radar_metrics + [radar_metrics[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values, theta=labels,
                    fill='toself', name=row['Player'],
                    line=dict(color=radar_colors[i % len(radar_colors)], width=2),
                    opacity=0.6
                ))

            fig_radar.update_layout(
                paper_bgcolor=CHART_PAPER,
                polar=dict(
                    bgcolor=CHART_BG,
                    radialaxis=dict(
                        visible=True, range=[0, 100], gridcolor=CHART_GRID,
                        tickfont=dict(color="#241414")
                    ),
                    angularaxis=dict(tickfont=dict(color="#241414"))
                ),
                font=CHART_FONT,
                height=480,
                legend=dict(bgcolor='rgba(255,255,255,0.6)', bordercolor=CHART_GRID, borderwidth=1, font=dict(color="#241414")),
                title=dict(
                    text="Normalized Performance Radar (0 = lowest on shortlist, 100 = highest)",
                    font=dict(family="Libre Caslon Text, serif", color="#241414", size=16)
                ),
                transition=dict(duration=400, easing="cubic-in-out")
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Clear Entire Shortlist"):
        st.session_state.shortlist = []
        st.rerun()