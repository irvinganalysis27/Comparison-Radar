# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# ------------- App setup -------------
st.set_page_config(page_title="Radar App", page_icon="⚽", layout="wide")

PASSWORD = "cowboy"
st.title("⚽ Radar App")

pwd = st.text_input("Enter password:", type="password", key="pwd_main")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# ------------- Sidebar "pages" -------------
page = st.sidebar.radio("View", ["Single Player Radar", "Comparison Radar"], key="page_picker")

# ------------- 6-position mapping -------------
SIX_GROUPS = [
    "Goalkeeper", "Wide Defender", "Central Defender",
    "Central Midfielder", "Wide Midfielder", "Central Forward"
]

RAW_TO_SIX = {
    # GK
    "GK":"Goalkeeper","GKP":"Goalkeeper","GOALKEEPER":"Goalkeeper",
    # Wide Def
    "RB":"Wide Defender","LB":"Wide Defender","RWB":"Wide Defender","LWB":"Wide Defender",
    "RFB":"Wide Defender","LFB":"Wide Defender",
    # CB
    "CB":"Central Defender","RCB":"Central Defender","LCB":"Central Defender",
    "CBR":"Central Defender","CBL":"Central Defender","SW":"Central Defender",
    # CM
    "CMF":"Central Midfielder","CM":"Central Midfielder",
    "RCMF":"Central Midfielder","RCM":"Central Midfielder",
    "LCMF":"Central Midfielder","LCM":"Central Midfielder",
    "DMF":"Central Midfielder","DM":"Central Midfielder","CDM":"Central Midfielder",
    "RDMF":"Central Midfielder","RDM":"Central Midfielder",
    "LDMF":"Central Midfielder","LDM":"Central Midfielder",
    "AMF":"Central Midfielder","AM":"Central Midfielder","CAM":"Central Midfielder",
    "SS":"Central Midfielder","10":"Central Midfielder",
    # Wide Mid
    "LWF":"Wide Midfielder","RWF":"Wide Midfielder","RW":"Wide Midfielder","LW":"Wide Midfielder",
    "LAMF":"Wide Midfielder","RAMF":"Wide Midfielder","RM":"Wide Midfielder","LM":"Wide Midfielder",
    "WF":"Wide Midfielder","RWG":"Wide Midfielder","LWG":"Wide Midfielder","W":"Wide Midfielder",
    # CF
    "CF":"Central Forward","ST":"Central Forward","9":"Central Forward",
    "FW":"Central Forward","STK":"Central Forward","CFW":"Central Forward"
}

def _clean_pos_token(tok: str) -> str:
    if pd.isna(tok): return ""
    t = str(tok).upper().replace(".", "").replace("-", "").replace(" ", "")
    return t

def parse_first_position(cell) -> str:
    if pd.isna(cell): return ""
    first = re.split(r"[,/]", str(cell))[0].strip()
    return _clean_pos_token(first)

def map_first_position_to_group(cell) -> str:
    tok = parse_first_position(cell)
    return RAW_TO_SIX.get(tok, "Wide Midfielder")

# ------------- Default template per group -------------
DEFAULT_TEMPLATE = {
    "Goalkeeper": "Goalkeeper",
    "Wide Defender": "Wide Defender, Full Back",
    "Central Defender": "Central Defender, All Round",
    "Central Midfielder": "Central Midfielder, All Round CM",
    "Wide Midfielder": "Wide Midfielder, Touchline Winger",
    "Central Forward": "Striker, All Round CF"
}

# ------------- Templates / metrics -------------
position_metrics = {
    # ===== GK =====
    "Goalkeeper": {
        "metrics": [
            "Clean sheets per 90", "Conceded goals per 90", "Prevented goals per 90",
            "Save rate, %", "Shots against per 90", "Aerial duels per 90", "Exits per 90",
            "Passes per 90", "Accurate passes, %", "Short / medium passes per 90",
            "Accurate short / medium passes, %", "Long passes per 90", "Accurate long passes, %"
        ],
        "groups": {
            "Clean sheets per 90":"Goalkeeping",
            "Conceded goals per 90":"Goalkeeping",
            "Prevented goals per 90":"Goalkeeping",
            "Save rate, %":"Goalkeeping",
            "Shots against per 90":"Goalkeeping",
            "Aerial duels per 90":"Goalkeeping",
            "Exits per 90":"Goalkeeping",
            "Passes per 90":"Possession",
            "Accurate passes, %":"Possession",
            "Short / medium passes per 90":"Possession",
            "Accurate short / medium passes, %":"Possession",
            "Long passes per 90":"Possession",
            "Accurate long passes, %":"Possession"
        }
    },

    # ===== CBs =====
    "Central Defender, Ball Winning": {
        "metrics": [
            "Defensive duels per 90","Defensive duels won, %","Aerial duels per 90","Aerial duels won, %",
            "Shots blocked per 90","PAdj Interceptions","Head goals per 90",
            "Successful dribbles, %","Accurate passes, %"
        ],
        "groups": {
            "Defensive duels per 90":"Defensive",
            "Defensive duels won, %":"Defensive",
            "Aerial duels per 90":"Defensive",
            "Aerial duels won, %":"Defensive",
            "Shots blocked per 90":"Defensive",
            "PAdj Interceptions":"Defensive",
            "Head goals per 90":"Attacking",
            "Successful dribbles, %":"Possession",
            "Accurate passes, %":"Possession"
        }
    },
    "Central Defender, Ball Playing": {
        "metrics": [
            "Defensive duels per 90","Defensive duels won, %","Shots blocked per 90","PAdj Interceptions",
            "Forward passes per 90","Accurate forward passes, %","Passes to final third per 90",
            "Accurate passes to final third, %","Accurate passes, %","Dribbles per 90","Successful dribbles, %"
        ],
        "groups": {
            "Defensive duels per 90":"Defensive","Defensive duels won, %":"Defensive",
            "Shots blocked per 90":"Defensive","PAdj Interceptions":"Defensive",
            "Forward passes per 90":"Possession","Accurate forward passes, %":"Possession",
            "Passes to final third per 90":"Possession","Accurate passes to final third, %":"Possession",
            "Accurate passes, %":"Possession","Dribbles per 90":"Possession","Successful dribbles, %":"Possession"
        }
    },
    "Central Defender, All Round": {
        "metrics": [
            "Defensive duels per 90","Defensive duels won, %","Aerial duels per 90","Aerial duels won, %",
            "Shots blocked per 90","PAdj Interceptions","Accurate passes, %",
            "Forward passes per 90","Accurate forward passes, %","Passes to final third per 90",
            "Accurate passes to final third, %","Dribbles per 90","Successful dribbles, %"
        ],
        "groups": {
            "Defensive duels per 90":"Defensive","Defensive duels won, %":"Defensive",
            "Aerial duels per 90":"Defensive","Aerial duels won, %":"Defensive",
            "Shots blocked per 90":"Defensive","PAdj Interceptions":"Defensive",
            "Accurate passes, %":"Possession","Forward passes per 90":"Possession",
            "Accurate forward passes, %":"Possession","Passes to final third per 90":"Possession",
            "Accurate passes to final third, %":"Possession","Dribbles per 90":"Possession","Successful dribbles, %":"Possession"
        }
    },

    # ===== Wide Def =====
    "Wide Defender, Full Back": {
        "metrics": [
            "Successful defensive actions per 90","Defensive duels per 90","Defensive duels won, %",
            "PAdj Interceptions","Crosses per 90","Accurate crosses, %","Passes to final third per 90",
            "Accurate passes to final third, %","Dribbles per 90","Successful dribbles, %","xA per 90","Assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90":"Defensive","Defensive duels per 90":"Defensive",
            "Defensive duels won, %":"Defensive","PAdj Interceptions":"Defensive",
            "Crosses per 90":"Possession","Accurate crosses, %":"Possession",
            "Passes to final third per 90":"Possession","Accurate passes to final third, %":"Possession",
            "Dribbles per 90":"Possession","Successful dribbles, %":"Possession",
            "xA per 90":"Attacking","Assists per 90":"Attacking"
        }
    },
    "Wide Defender, Wing Back": {
        "metrics": [
            "Successful defensive actions per 90","Defensive duels per 90","Defensive duels won, %",
            "Dribbles per 90","Successful dribbles, %","Offensive duels per 90","Offensive duels won, %",
            "Crosses per 90","Accurate crosses, %","Passes to final third per 90",
            "xA per 90","Assists per 90","Shot assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90":"Defensive","Defensive duels per 90":"Defensive",
            "Defensive duels won, %":"Defensive","Dribbles per 90":"Possession","Successful dribbles, %":"Possession",
            "Offensive duels per 90":"Possession","Offensive duels won, %":"Possession",
            "Crosses per 90":"Possession","Accurate crosses, %":"Possession",
            "Passes to final third per 90":"Possession","xA per 90":"Attacking",
            "Assists per 90":"Attacking","Shot assists per 90":"Attacking"
        }
    },
    "Wide Defender, Inverted": {
        "metrics": [
            "Successful defensive actions per 90","Defensive duels per 90","Defensive duels won, %",
            "PAdj Interceptions","Forward passes per 90","Accurate forward passes, %",
            "Through passes per 90","Accurate through passes, %","Passes to final third per 90",
            "Accurate passes to final third, %","xA per 90","Assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90":"Defensive","Defensive duels per 90":"Defensive",
            "Defensive duels won, %":"Defensive","PAdj Interceptions":"Defensive",
            "Forward passes per 90":"Possession","Accurate forward passes, %":"Possession",
            "Through passes per 90":"Possession","Accurate through passes, %":"Possession",
            "Passes to final third per 90":"Possession","Accurate passes to final third, %":"Possession",
            "xA per 90":"Attacking","Assists per 90":"Attacking"
        }
    },

    # ===== CM =====
    "Central Midfielder, Creative": {
        "metrics": [
            "Non-penalty goals per 90","xG per 90","Goal conversion, %","Assists per 90","xA per 90",
            "Shots per 90","Shots on target, %","Forward passes per 90","Accurate forward passes, %",
            "Through passes per 90","Accurate through passes, %","Dribbles per 90","Successful dribbles, %"
        ],
        "groups": {
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Goal conversion, %":"Attacking",
            "Assists per 90":"Attacking","xA per 90":"Attacking","Shots per 90":"Attacking",
            "Shots on target, %":"Attacking","Forward passes per 90":"Possession",
            "Accurate forward passes, %":"Possession","Through passes per 90":"Possession",
            "Accurate through passes, %":"Possession","Dribbles per 90":"Possession","Successful dribbles, %":"Possession"
        }
    },
    "Central Midfielder, Defensive": {
        "metrics": [
            "Successful defensive actions per 90","Defensive duels per 90","Defensive duels won, %",
            "Aerial duels per 90","Aerial duels won, %","PAdj Interceptions","Successful dribbles, %",
            "Offensive duels per 90","Offensive duels won, %","Accurate passes, %","Forward passes per 90",
            "Accurate forward passes, %","Passes to final third per 90","Accurate passes to final third, %"
        ],
        "groups": {
            "Successful defensive actions per 90":"Defensive","Defensive duels per 90":"Defensive",
            "Defensive duels won, %":"Defensive","Aerial duels per 90":"Defensive",
            "Aerial duels won, %":"Defensive","PAdj Interceptions":"Defensive",
            "Successful dribbles, %":"Possession","Offensive duels per 90":"Possession",
            "Offensive duels won, %":"Possession","Accurate passes, %":"Possession",
            "Forward passes per 90":"Possession","Accurate forward passes, %":"Possession",
            "Passes to final third per 90":"Possession","Accurate passes to final third, %":"Possession"
        }
    },
    "Central Midfielder, All Round CM": {
        "metrics": [
            "Non-penalty goals per 90","xG per 90","Goal conversion, %","Assists per 90","xA per 90",
            "Shots per 90","Shots on target, %","Forward passes per 90","Accurate forward passes, %",
            "Passes to final third per 90","Accurate passes to final third, %","Dribbles per 90","Successful dribbles, %",
            "Successful defensive actions per 90","Defensive duels per 90","Defensive duels won, %","PAdj Interceptions"
        ],
        "groups": {
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Goal conversion, %":"Attacking",
            "Assists per 90":"Attacking","xA per 90":"Attacking","Shots per 90":"Attacking",
            "Shots on target, %":"Attacking","Forward passes per 90":"Possession",
            "Accurate forward passes, %":"Possession","Passes to final third per 90":"Possession",
            "Accurate passes to final third, %":"Possession","Dribbles per 90":"Possession",
            "Successful dribbles, %":"Possession","Successful defensive actions per 90":"Defensive",
            "Defensive duels per 90":"Defensive","Defensive duels won, %":"Defensive","PAdj Interceptions":"Defensive"
        }
    },

    # ===== Wingers =====
    "Wide Midfielder, Touchline Winger": {
        "metrics": [
            "Non-penalty goals per 90","xG per 90","Assists per 90","xA per 90","Crosses per 90",
            "Accurate crosses, %","Dribbles per 90","Successful dribbles, %","Fouls suffered per 90",
            "Shot assists per 90","Passes to penalty area per 90","Accurate passes to penalty area, %"
        ],
        "groups": {
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Assists per 90":"Attacking",
            "xA per 90":"Attacking","Crosses per 90":"Possession","Accurate crosses, %":"Possession",
            "Dribbles per 90":"Possession","Successful dribbles, %":"Possession","Fouls suffered per 90":"Possession",
            "Shot assists per 90":"Possession","Passes to penalty area per 90":"Possession",
            "Accurate passes to penalty area, %":"Possession"
        }
    },
    "Wide Midfielder, Inverted Winger": {
        "metrics": [
            "Non-penalty goals per 90","xG per 90","Shots per 90","Shots on target, %","Goal conversion, %",
            "Assists per 90","xA per 90","Dribbles per 90","Successful dribbles, %","Fouls suffered per 90",
            "Shot assists per 90","Passes to penalty area per 90","Accurate passes to penalty area, %","Deep completions per 90"
        ],
        "groups": {
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Shots per 90":"Attacking",
            "Shots on target, %":"Attacking","Goal conversion, %":"Attacking","Assists per 90":"Attacking",
            "xA per 90":"Attacking","Dribbles per 90":"Possession","Successful dribbles, %":"Possession",
            "Fouls suffered per 90":"Possession","Shot assists per 90":"Possession",
            "Passes to penalty area per 90":"Possession","Accurate passes to penalty area, %":"Possession",
            "Deep completions per 90":"Possession"
        }
    },
    "Wide Midfielder, Defensive Wide Midfielder": {
        "metrics": [
            "Non-penalty goals per 90","xG per 90","Shots per 90","Shots on target, %","Assists per 90","xA per 90",
            "Crosses per 90","Accurate crosses, %","Dribbles per 90","Successful dribbles, %","Fouls suffered per 90",
            "Shot assists per 90","Successful defensive actions per 90","Defensive duels won, %","PAdj Interceptions"
        ],
        "groups": {
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Shots per 90":"Attacking",
            "Shots on target, %":"Attacking","Assists per 90":"Attacking","xA per 90":"Attacking",
            "Crosses per 90":"Possession","Accurate crosses, %":"Possession","Dribbles per 90":"Possession",
            "Successful dribbles, %":"Possession","Fouls suffered per 90":"Possession","Shot assists per 90":"Possession",
            "Successful defensive actions per 90":"Defensive","Defensive duels won, %":"Defensive","PAdj Interceptions":"Defensive"
        }
    },

    # ===== Strikers =====
    "Striker, Number 10": {
        "metrics": [
            "Successful defensive actions per 90","Non-penalty goals per 90","xG per 90","Shots per 90","Shots on target, %",
            "Goal conversion, %","Assists per 90","xA per 90","Shot assists per 90","Forward passes per 90",
            "Accurate forward passes, %","Passes to final third per 90","Accurate passes to final third, %","Through passes per 90","Accurate through passes, %"
        ],
        "groups": {
            "Successful defensive actions per 90":"Off The Ball","Non-penalty goals per 90":"Attacking","xG per 90":"Attacking",
            "Shots per 90":"Attacking","Shots on target, %":"Attacking","Goal conversion, %":"Attacking","Assists per 90":"Attacking",
            "xA per 90":"Attacking","Shot assists per 90":"Attacking","Forward passes per 90":"Possession",
            "Accurate forward passes, %":"Possession","Passes to final third per 90":"Possession","Accurate passes to final third, %":"Possession",
            "Through passes per 90":"Possession","Accurate through passes, %":"Possession"
        }
    },
    "Striker, Target Man": {
        "metrics": [
            "Aerial duels per 90","Aerial duels won, %","Non-penalty goals per 90","xG per 90","Shots per 90","Shots on target, %",
            "Goal conversion, %","Head goals per 90","Assists per 90","xA per 90","Shot assists per 90",
            "Offensive duels per 90","Offensive duels won, %","Passes to penalty area per 90","Accurate passes to penalty area, %"
        ],
        "groups": {
            "Aerial duels per 90":"Off The Ball","Aerial duels won, %":"Off The Ball","Non-penalty goals per 90":"Attacking",
            "xG per 90":"Attacking","Shots per 90":"Attacking","Shots on target, %":"Attacking","Goal conversion, %":"Attacking",
            "Head goals per 90":"Attacking","Assists per 90":"Attacking","xA per 90":"Attacking","Shot assists per 90":"Attacking",
            "Offensive duels per 90":"Possession","Offensive duels won, %":"Possession",
            "Passes to penalty area per 90":"Possession","Accurate passes to penalty area, %":"Possession"
        }
    },
    "Striker, Penalty Box Striker": {
        "metrics": [
            "Non-penalty goals per 90","xG per 90","Shots per 90","Shots on target, %","Goal conversion, %",
            "Shot assists per 90","Touches in penalty area per 90","Offensive duels per 90","Offensive duels won, %",
            "Dribbles per 90","Successful dribbles, %"
        ],
        "groups": {
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Shots per 90":"Attacking",
            "Shots on target, %":"Attacking","Goal conversion, %":"Attacking","Shot assists per 90":"Attacking",
            "Touches in penalty area per 90":"Attacking","Offensive duels per 90":"Possession",
            "Offensive duels won, %":"Possession","Dribbles per 90":"Possession","Successful dribbles, %":"Possession"
        }
    },
    "Striker, All Round CF": {
        "metrics": [
            "Successful defensive actions per 90","Aerial duels per 90","Aerial duels won, %","Non-penalty goals per 90",
            "xG per 90","Shots per 90","Shots on target, %","Goal conversion, %","Assists per 90","xA per 90",
            "Shot assists per 90","Offensive duels per 90","Offensive duels won, %"
        ],
        "groups": {
            "Successful defensive actions per 90":"Off The Ball","Aerial duels per 90":"Off The Ball","Aerial duels won, %":"Off The Ball",
            "Non-penalty goals per 90":"Attacking","xG per 90":"Attacking","Shots per 90":"Attacking","Shots on target, %":"Attacking",
            "Goal conversion, %":"Attacking","Assists per 90":"Attacking","xA per 90":"Attacking","Shot assists per 90":"Attacking",
            "Offensive duels per 90":"Possession","Offensive duels won, %":"Possession"
        }
    },
    "Striker, Pressing Forward": {
        "metrics": [
            "Successful defensive actions per 90","Defensive duels per 90","Defensive duels won, %","Aerial duels per 90",
            "Aerial duels won, %","PAdj Interceptions","Offensive duels per 90","Offensive duels won, %",
            "Dribbles per 90","Successful dribbles, %","Forward passes per 90","Accurate forward passes, %",
            "xA per 90","Shot assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90":"Off The Ball","Defensive duels per 90":"Off The Ball",
            "Defensive duels won, %":"Off The Ball","Aerial duels per 90":"Off The Ball",
            "Aerial duels won, %":"Off The Ball","PAdj Interceptions":"Off The Ball",
            "Offensive duels per 90":"Possession","Offensive duels won, %":"Possession",
            "Dribbles per 90":"Possession","Successful dribbles, %":"Possession",
            "Forward passes per 90":"Possession","Accurate forward passes, %":"Possession",
            "xA per 90":"Attacking","Shot assists per 90":"Attacking"
        }
    }
}

group_colors = {
    "Off The Ball": "crimson",
    "Attacking": "royalblue",
    "Possession": "seagreen",
    "Defensive": "darkorange",
    "Goalkeeping": "purple"
}

# ------------- Shared uploader (one widget only) -------------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"], key="uploader_main")
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# Positions / 6-group column
if "Position" in df.columns:
    df["Positions played"] = df["Position"].astype(str)
else:
    df["Positions played"] = np.nan
df["Six-Group Position"] = df["Position"].apply(map_first_position_to_group) if "Position" in df.columns else np.nan

# Minutes filter
minutes_col = "Minutes played"
min_minutes = st.number_input("Minimum minutes to include", min_value=0, value=800, step=50, key="mins_box")
df["_minutes_numeric"] = pd.to_numeric(df.get(minutes_col, np.nan), errors="coerce")
df = df[df["_minutes_numeric"] >= min_minutes].copy()
if df.empty:
    st.warning("No players meet the minutes threshold.")
    st.stop()

# Age filter
if "Age" in df.columns:
    df["_age_numeric"] = pd.to_numeric(df["Age"], errors="coerce")
    if df["_age_numeric"].notna().any():
        age_min = int(np.nanmin(df["_age_numeric"])); age_max = int(np.nanmax(df["_age_numeric"]))
        sel_min, sel_max = st.slider("Age range", min_value=age_min, max_value=age_max, value=(age_min, age_max), step=1, key="age_slider")
        df = df[df["_age_numeric"].between(sel_min, sel_max)].copy()
st.caption(f"Filtered by minutes ≥ {min_minutes}. Players remaining, {len(df)}")

# 6-group filter (collapsed title)
available_groups = [g for g in SIX_GROUPS if g in df["Six-Group Position"].unique()]
selected_groups = st.multiselect("Include groups", options=available_groups, default=[], label_visibility="collapsed", key="sixgroup_multi")
if selected_groups:
    df = df[df["Six-Group Position"].isin(selected_groups)].copy()
    if df.empty:
        st.warning("No players after 6-group filter.")
        st.stop()

# ---------- Helper: compute percentiles like original (within filtered df) ----------
def compute_percentiles_for(metrics_list, data):
    metrics_df = data[metrics_list].copy()
    percentiles = (metrics_df.rank(pct=True) * 100).round(1)
    return metrics_df, percentiles

# ---------- Single Player Radar PAGE ----------
if page == "Single Player Radar":

    # ---- Session state for stickiness ----
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = None
    if "prev_groups_sig" not in st.session_state:
        st.session_state.prev_groups_sig = None

    # If group filter changed, snap template to that group's default
    groups_sig = tuple(sorted(selected_groups)) if selected_groups else ("ALL",)
    if st.session_state.prev_groups_sig != groups_sig:
        # pick a representative player's group if subset chosen; else do nothing special
        if selected_groups:
            grp = selected_groups[0]
            st.session_state.selected_template = DEFAULT_TEMPLATE.get(grp, list(position_metrics.keys())[0])
        st.session_state.prev_groups_sig = groups_sig

    # Build player list
    players = df["Player"].dropna().unique().tolist()
    if not players:
        st.warning("No players available.")
        st.stop()

    # Keep previous player if still present
    if st.session_state.selected_player not in players:
        st.session_state.selected_player = players[0]

    selected_player = st.selectbox("Choose a player", players,
                                   index=players.index(st.session_state.selected_player),
                                   key="single_player_select")
    st.session_state.selected_player = selected_player

    # Determine a sensible default template if none picked yet
    if st.session_state.selected_template is None:
        try:
            p_group = df.loc[df["Player"] == selected_player, "Six-Group Position"].iloc[0]
            st.session_state.selected_template = DEFAULT_TEMPLATE.get(p_group, list(position_metrics.keys())[0])
        except Exception:
            st.session_state.selected_template = list(position_metrics.keys())[0]

    # Template selector (manual change allowed; won't change when player changes)
    tmpl_names = list(position_metrics.keys())
    tmpl_index = tmpl_names.index(st.session_state.selected_template) if st.session_state.selected_template in tmpl_names else 0
    selected_template = st.selectbox("Choose a position template for the chart", tmpl_names, index=tmpl_index, key="single_template_select")
    st.session_state.selected_template = selected_template

    metrics = position_metrics[selected_template]["metrics"]
    metric_groups = position_metrics[selected_template]["groups"]

    # Ensure columns exist & are numeric
    for m in metrics:
        if m not in df.columns:
            df[m] = 0
    df[metrics] = df[metrics].fillna(0)

    # ---------- Essential Criteria (multiple AND rules) ----------
    with st.expander("Essential Criteria", expanded=False):
        use_all_cols = st.checkbox("Pick from all numeric columns", value=False, help="Unchecked, only metrics in the selected template are shown", key="ec_allcols")
        numeric_cols_all = sorted([c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])])
        metric_pool = numeric_cols_all if use_all_cols else metrics

        if "ec_rows" not in st.session_state:
            st.session_state.ec_rows = 1

        cbtn1, cbtn2, cbtn3 = st.columns(3)
        with cbtn1:
            if st.button("Add criterion"):
                st.session_state.ec_rows += 1
        with cbtn2:
            if st.button("Remove last", disabled=st.session_state.ec_rows <= 1):
                st.session_state.ec_rows = max(1, st.session_state.ec_rows - 1)
        with cbtn3:
            apply_all = st.checkbox("Apply all criteria", value=False, key="ec_apply")

        criteria = []
        for i in range(st.session_state.ec_rows):
            st.markdown(f"**Criterion {i+1}**")
            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])

            with c1:
                metric_name = st.selectbox("Metric", metric_pool, key=f"ec_metric_{i}")
            with c2:
                mode = st.radio("Apply to", ["Raw", "Percentile"], horizontal=True, key=f"ec_mode_{i}")
            with c3:
                op = st.selectbox("Operator", [">=", ">", "<=", "<"], index=0, key=f"ec_op_{i}")
            with c4:
                if mode == "Percentile":
                    default_thr = 50.0
                else:
                    default_thr = float(np.nanmedian(pd.to_numeric(df[metric_name], errors="coerce")))
                    if not np.isfinite(default_thr): default_thr = 0.0
                thr = st.number_input("Threshold", value=float(default_thr), key=f"ec_thr_{i}")
            criteria.append((metric_name, mode, op, thr))

        if apply_all and criteria:
            temp_cols = []
            mask_all = pd.Series(True, index=df.index)
            for metric_name, mode, op, thr in criteria:
                if mode == "Percentile":
                    df[metric_name] = pd.to_numeric(df[metric_name], errors="coerce")
                    perc_series = (df[metric_name].rank(pct=True) * 100).round(1)
                    tmp_col = f"__tmp__{metric_name}"
                    df[tmp_col] = perc_series
                    col = tmp_col
                    temp_cols.append(tmp_col)
                else:
                    col = metric_name
                    df[col] = pd.to_numeric(df[col], errors="coerce")

                if op == ">=": m = df[col] >= thr
                elif op == ">": m = df[col] > thr
                elif op == "<=": m = df[col] <= thr
                else: m = df[col] < thr
                mask_all &= m

            kept = int(mask_all.sum()); dropped = int((~mask_all).sum())
            df = df[mask_all].copy()
            if temp_cols:
                df.drop(columns=temp_cols, inplace=True, errors="ignore")
            st.caption(f"Essential Criteria applied. Kept {kept}, removed {dropped} players.")

    # Rebuild player list after EC filter (and keep selection if possible)
    players = df["Player"].dropna().unique().tolist()
    if not players:
        st.warning("No players left after filters.")
        st.stop()
    if st.session_state.selected_player not in players:
        st.session_state.selected_player = players[0]
    selected_player = st.selectbox("Choose a player (after filters)", players,
                                   index=players.index(st.session_state.selected_player),
                                   key="single_player_select_after")
    st.session_state.selected_player = selected_player

    # Percentiles within *current filtered df* (exactly like original)
    raw_df, pct_df = compute_percentiles_for(metrics, df)

    keep_cols = ["Player","Team within selected timeframe","Team","Age","Height","Positions played","Minutes played"]
    plot_data = pd.concat([df[keep_cols].reset_index(drop=True),
                           raw_df.reset_index(drop=True),
                           pct_df.add_suffix(" (percentile)").reset_index(drop=True)], axis=1)

    # Z-score average for ranking table
    sel_metrics = list(position_metrics[selected_template]["groups"].keys())
    pct_cols = [m + " (percentile)" for m in sel_metrics]
    z_scores_all = (plot_data[pct_cols] - 50) / 15
    plot_data["Avg Z Score"] = z_scores_all.mean(axis=1)
    plot_data["Rank"] = plot_data["Avg Z Score"].rank(ascending=False, method="min").astype(int)

    def plot_radial_bar_grouped(player_name, plot_df, metric_groups, colors_map):
        row = plot_df[plot_df["Player"] == player_name]
        if row.empty:
            st.error(f"No player named '{player_name}' found.")
            return
        sel_metrics_loc = list(metric_groups.keys())
        raw = row[sel_metrics_loc].values.flatten()
        percentiles = row[[m + " (percentile)" for m in sel_metrics_loc]].values.flatten()
        groups = [metric_groups[m] for m in sel_metrics_loc]
        colors = [colors_map[g] for g in groups]

        num_bars = len(sel_metrics_loc)
        angles = np.linspace(0, 2*np.pi, num_bars, endpoint=False)

        fig, ax = plt.subplots(figsize=(10,10), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor("white"); ax.set_facecolor("white")
        ax.set_theta_offset(np.pi/2); ax.set_theta_direction(-1)
        ax.set_ylim(0,100); ax.set_yticklabels([]); ax.set_xticks([]); ax.spines["polar"].set_visible(False)

        ax.bar(angles, percentiles, width=2*np.pi/num_bars*0.9, color=colors, edgecolor=colors, alpha=0.75)

        for angle, raw_val in zip(angles, raw):
            ax.text(angle, 50, f"{raw_val:.2f}", ha="center", va="center", color="black", fontsize=10, fontweight="bold")

        for i, angle in enumerate(angles):
            label = sel_metrics_loc[i].replace(" per 90","").replace(", %"," (%)")
            ax.text(angle, 108, label, ha="center", va="center", color="black", fontsize=10, fontweight="bold")

        # group headings
        pos = {}
        for g, a in zip(groups, angles): pos.setdefault(g, []).append(a)
        for g, arr in pos.items():
            ax.text(np.mean(arr), 125, g, ha="center", va="center", fontsize=20, fontweight="bold", color=colors_map[g])

        age = row["Age"].values[0]; height = row["Height"].values[0]
        team = row["Team within selected timeframe"].values[0]
        mins = row["Minutes played"].values[0] if "Minutes played" in row else np.nan
        rank_val = int(row["Rank"].values[0]) if "Rank" in row else None

        parts = [player_name]
        if pd.notnull(age): parts.append(f"{int(age)} years old")
        if pd.notnull(height): parts.append(f"{int(height)} cm")
        line1 = " | ".join(parts)
        line2 = " | ".join([p for p in [str(team) if pd.notnull(team) else "", f"{int(mins)} mins" if pd.notnull(mins) else "", f"Rank #{rank_val}" if rank_val is not None else ""] if p])

        ax.set_title(f"{line1}\n{line2}", color="black", size=22, pad=20, y=1.12)

        z_scores = (percentiles - 50) / 15
        avg_z = float(np.mean(z_scores))
        if avg_z >= 1.0: badge=("Excellent","#228B22")
        elif avg_z >= 0.3: badge=("Good","#1E90FF")
        elif avg_z >= -0.3: badge=("Average","#DAA520")
        else: badge=("Below Average","#DC143C")
        st.markdown(
            f"<div style='text-align:center; margin-top: 20px;'>"
            f"<span style='font-size:24px; font-weight:bold;'>Average Z Score, {avg_z:.2f}</span><br>"
            f"<span style='background-color:{badge[1]}; color:white; padding:5px 10px; border-radius:8px; font-size:20px;'>{badge[0]}</span></div>",
            unsafe_allow_html=True
        )
        st.pyplot(fig)

    plot_radial_bar_grouped(st.session_state.selected_player, plot_data,
                            position_metrics[selected_template]["groups"], group_colors)

    # Ranking table
    st.markdown("### Players Ranked by Z-Score")
    cols_for_table = ["Player","Positions played","Age","Team","Team within selected timeframe","Minutes played","Avg Z Score","Rank"]
    z_ranking = (plot_data[cols_for_table].sort_values(by="Avg Z Score", ascending=False).reset_index(drop=True))
    z_ranking[["Team","Team within selected timeframe"]] = z_ranking[["Team","Team within selected timeframe"]].fillna("N/A")
    if "Age" in z_ranking: z_ranking["Age"] = z_ranking["Age"].apply(lambda x: int(x) if pd.notnull(x) else x)
    z_ranking.index = np.arange(1, len(z_ranking)+1); z_ranking.index.name = "Row"
    st.dataframe(z_ranking, use_container_width=True)

# ---------- Comparison PAGE ----------
else:
    # Keep one template picker here; defaults by first player's group if possible
    comp_players = df["Player"].dropna().unique().tolist()
    if not comp_players:
        st.warning("No players available.")
        st.stop()

    left, right = st.columns(2)
    with left:
        p1 = st.selectbox("Player A", comp_players, key="comp_p1")
    with right:
        p2 = st.selectbox("Player B (optional)", ["(none)"] + comp_players, key="comp_p2")
    if p2 == "(none)": p2 = None

    # Template default from p1's group if available
    try:
        p1_group = df.loc[df["Player"] == p1, "Six-Group Position"].iloc[0]
        default_comp_template = DEFAULT_TEMPLATE.get(p1_group, list(position_metrics.keys())[0])
    except Exception:
        default_comp_template = list(position_metrics.keys())[0]

    comp_tmpl_names = list(position_metrics.keys())
    comp_tmpl_index = comp_tmpl_names.index(default_comp_template) if default_comp_template in comp_tmpl_names else 0
    comp_template = st.selectbox("Choose a position template", comp_tmpl_names, index=comp_tmpl_index, key="comp_template")

    comp_metrics = position_metrics[comp_template]["metrics"]
    # Ensure columns numeric / present
    for m in comp_metrics:
        if m not in df.columns: df[m] = 0
    df[comp_metrics] = df[comp_metrics].fillna(0)

    # Percentiles within current filtered df (same as single page)
    raw_df_c, pct_df_c = compute_percentiles_for(comp_metrics, df)

    # Pull two rows
    def get_row(player_name):
        ix = df.index[df["Player"] == player_name]
        if len(ix) == 0: return None
        r = pct_df_c.loc[ix[0], :].values.astype(float)  # percentiles
        return r

    r1 = get_row(p1); r2 = get_row(p2) if p2 else None
    if r1 is None:
        st.error("Player A not found after filters.")
        st.stop()

    # Radar (lines + fill)
    labels = [m.replace(" per 90","").replace(", %"," (%)") for m in comp_metrics]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    values1 = r1; values1 = np.concatenate([values1, values1[:1]])
    angles_full = np.concatenate([angles, angles[:1]])

    fig, ax = plt.subplots(figsize=(10,10), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi/2); ax.set_theta_direction(-1)
    ax.set_ylim(0,100); ax.set_yticks([20,40,60,80]); ax.grid(True, alpha=0.25)

    # Labels
    ax.set_xticks(angles); ax.set_xticklabels(labels, fontsize=10)

    # Player A (blue)
    ax.plot(angles_full, values1, linewidth=2.5, label=p1, color="#1f77b4")
    ax.fill(angles_full, values1, alpha=0.25, color="#1f77b4")

    # Player B (red) optional
    if r2 is not None:
        v2 = np.concatenate([r2, r2[:1]])
        ax.plot(angles_full, v2, linewidth=2.5, label=p2, color="#d62728")
        ax.fill(angles_full, v2, alpha=0.20, color="#d62728")

    # Title "A vs B" with colored names
    title = f"$\\bf{{\\color{{#1f77b4}}{p1}}}$"
    if p2: title += f" vs $\\bf{{\\color{{#d62728}}{p2}}}$"
    ax.set_title(title, fontsize=20, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
    st.pyplot(fig)
