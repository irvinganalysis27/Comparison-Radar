    # app.py — Comparison Radar with genre background shading
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Comparison Radar", layout="centered")

# ------------------------ Basic password ------------------------
PASSWORD = "cowboy"
st.title("⚽ Comparison Radar")

pwd = st.text_input("Enter password:", type="password")
if pwd != PASSWORD:
    st.warning("Please enter the correct password to access the app.")
    st.stop()

# ------------------------ Position groups & mapping -------------------
SIX_GROUPS = [
    "Goalkeeper",
    "Wide Defender",
    "Central Defender",
    "Central Midfielder",
    "Wide Midfielder",
    "Central Forward",
]

RAW_TO_SIX = {
    # GK
    "GK": "Goalkeeper", "GKP": "Goalkeeper", "GOALKEEPER": "Goalkeeper",
    # Wide Defender
    "RB": "Wide Defender", "LB": "Wide Defender",
    "RWB": "Wide Defender", "LWB": "Wide Defender",
    "RFB": "Wide Defender", "LFB": "Wide Defender",
    # Central Defender
    "CB": "Central Defender", "RCB": "Central Defender", "LCB": "Central Defender",
    "CBR": "Central Defender", "CBL": "Central Defender", "SW": "Central Defender",
    # Central Midfielder
    "CMF": "Central Midfielder", "CM": "Central Midfielder",
    "RCMF": "Central Midfielder", "RCM": "Central Midfielder",
    "LCMF": "Central Midfielder", "LCM": "Central Midfielder",
    "DMF": "Central Midfielder", "DM": "Central Midfielder", "CDM": "Central Midfielder",
    "RDMF": "Central Midfielder", "RDM": "Central Midfielder",
    "LDMF": "Central Midfielder", "LDM": "Central Midfielder",
    "AMF": "Central Midfielder", "AM": "Central Midfielder", "CAM": "Central Midfielder",
    "SS": "Central Midfielder", "10": "Central Midfielder",
    # Wide Midfielder
    "LWF": "Wide Midfielder", "RWF": "Wide Midfielder",
    "RW": "Wide Midfielder", "LW": "Wide Midfielder",
    "LAMF": "Wide Midfielder", "RAMF": "Wide Midfielder",
    "RM": "Wide Midfielder", "LM": "Wide Midfielder",
    "WF": "Wide Midfielder", "RWG": "Wide Midfielder", "LWG": "Wide Midfielder", "W": "Wide Midfielder",
    # Central Forward
    "CF": "Central Forward", "ST": "Central Forward", "9": "Central Forward",
    "FW": "Central Forward", "STK": "Central Forward", "CFW": "Central Forward",
}

def _clean_pos_token(tok: str) -> str:
    if pd.isna(tok):
        return ""
    t = str(tok).upper()
    t = t.replace(".", "").replace("-", "").replace(" ", "")
    return t

def parse_first_position(cell) -> str:
    if pd.isna(cell):
        return ""
    first = re.split(r"[,/]", str(cell))[0].strip()
    return _clean_pos_token(first)

def map_first_position_to_group(cell) -> str:
    tok = parse_first_position(cell)
    return RAW_TO_SIX.get(tok, "Wide Midfielder")  # safe default

# ------------------------ Templates (same naming style as your other app) ---
position_metrics = {
    # ================== GOALKEEPER ==================
    "Goalkeeper": {
        "metrics": [
            "Clean sheets per 90", "Conceded goals per 90", "Prevented goals per 90",
            "Save rate, %", "Shots against per 90", "Aerial duels per 90", "Exits per 90",
            "Passes per 90", "Accurate passes, %", "Short / medium passes per 90",
            "Accurate short / medium passes, %", "Long passes per 90", "Accurate long passes, %"
        ],
        "groups": {
            "Clean sheets per 90": "Goalkeeping",
            "Conceded goals per 90": "Goalkeeping",
            "Prevented goals per 90": "Goalkeeping",
            "Save rate, %": "Goalkeeping",
            "Shots against per 90": "Goalkeeping",
            "Aerial duels per 90": "Goalkeeping",
            "Exits per 90": "Goalkeeping",
            "Passes per 90": "Possession",
            "Accurate passes, %": "Possession",
            "Short / medium passes per 90": "Possession",
            "Accurate short / medium passes, %": "Possession",
            "Long passes per 90": "Possession",
            "Accurate long passes, %": "Possession"
        }
    },

    # ================== CENTRAL DEFENDERS ==================
    "Central Defender, Ball Winning": {
        "metrics": [
            "Defensive duels per 90", "Defensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %",
            "Shots blocked per 90", "PAdj Interceptions",
            "Head goals per 90", "Successful dribbles, %", "Accurate passes, %"
        ],
        "groups": {
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Aerial duels per 90": "Defensive",
            "Aerial duels won, %": "Defensive",
            "Shots blocked per 90": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Head goals per 90": "Attacking",
            "Successful dribbles, %": "Possession",
            "Accurate passes, %": "Possession"
        }
    },
    "Central Defender, Ball Playing": {
        "metrics": [
            "Defensive duels per 90", "Defensive duels won, %",
            "Shots blocked per 90", "PAdj Interceptions",
            "Forward passes per 90", "Accurate forward passes, %",
            "Passes to final third per 90", "Accurate passes to final third, %",
            "Accurate passes, %", "Dribbles per 90", "Successful dribbles, %"
        ],
        "groups": {
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Shots blocked per 90": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession",
            "Accurate passes, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession"
        }
    },
    "Central Defender, All Round": {
        "metrics": [
            "Defensive duels per 90", "Defensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %",
            "Shots blocked per 90", "PAdj Interceptions",
            "Accurate passes, %", "Forward passes per 90", "Accurate forward passes, %",
            "Passes to final third per 90", "Accurate passes to final third, %",
            "Dribbles per 90", "Successful dribbles, %"
        ],
        "groups": {
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Aerial duels per 90": "Defensive",
            "Aerial duels won, %": "Defensive",
            "Shots blocked per 90": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Accurate passes, %": "Possession",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession"
        }
    },

    # ================== WIDE DEFENDERS ==================
    "Wide Defender, Full Back": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "PAdj Interceptions", "Crosses per 90", "Accurate crosses, %",
            "Passes to final third per 90", "Accurate passes to final third, %",
            "Dribbles per 90", "Successful dribbles, %",
            "xA per 90", "Assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Crosses per 90": "Possession",
            "Accurate crosses, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "xA per 90": "Attacking",
            "Assists per 90": "Attacking"
        }
    },
    "Wide Defender, Wing Back": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "Dribbles per 90", "Successful dribbles, %", "Offensive duels per 90", "Offensive duels won, %",
            "Crosses per 90", "Accurate crosses, %", "Passes to final third per 90",
            "xA per 90", "Assists per 90", "Shot assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "Crosses per 90": "Possession",
            "Accurate crosses, %": "Possession",
            "Passes to final third per 90": "Possession",
            "xA per 90": "Attacking",
            "Assists per 90": "Attacking",
            "Shot assists per 90": "Attacking"
        }
    },
    "Wide Defender, Inverted": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "PAdj Interceptions", "Forward passes per 90", "Accurate forward passes, %",
            "Through passes per 90", "Accurate through passes, %",
            "Passes to final third per 90", "Accurate passes to final third, %",
            "xA per 90", "Assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Through passes per 90": "Possession",
            "Accurate through passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession",
            "xA per 90": "Attacking",
            "Assists per 90": "Attacking"
        }
    },

    # ================== CENTRAL MIDFIELDERS ==================
    "Central Midfielder, Creative": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Goal conversion, %",
            "Assists per 90", "xA per 90", "Shots per 90", "Shots on target, %",
            "Forward passes per 90", "Accurate forward passes, %",
            "Through passes per 90", "Accurate through passes, %",
            "Dribbles per 90", "Successful dribbles, %"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Through passes per 90": "Possession",
            "Accurate through passes, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession"
        }
    },
    "Central Midfielder, Defensive": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %", "PAdj Interceptions",
            "Successful dribbles, %", "Offensive duels per 90", "Offensive duels won, %",
            "Accurate passes, %", "Forward passes per 90", "Accurate forward passes, %",
            "Passes to final third per 90", "Accurate passes to final third, %"
        ],
        "groups": {
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "Aerial duels per 90": "Defensive",
            "Aerial duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive",
            "Successful dribbles, %": "Possession",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "Accurate passes, %": "Possession",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession"
        }
    },
    "Central Midfielder, All Round CM": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Goal conversion, %",
            "Assists per 90", "xA per 90", "Shots per 90", "Shots on target, %",
            "Forward passes per 90", "Accurate forward passes, %",
            "Passes to final third per 90", "Accurate passes to final third, %",
            "Dribbles per 90", "Successful dribbles, %",
            "Successful defensive actions per 90", "Defensive duels per 90",
            "Defensive duels won, %", "PAdj Interceptions"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive"
        }
    },

    # ================== WIDE MIDFIELDERS ==================
    "Wide Midfielder, Touchline Winger": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Assists per 90", "xA per 90",
            "Crosses per 90", "Accurate crosses, %", "Dribbles per 90", "Successful dribbles, %",
            "Fouls suffered per 90", "Shot assists per 90",
            "Passes to penalty area per 90", "Accurate passes to penalty area, %"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Crosses per 90": "Possession",
            "Accurate crosses, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Fouls suffered per 90": "Possession",
            "Shot assists per 90": "Possession",
            "Passes to penalty area per 90": "Possession",
            "Accurate passes to penalty area, %": "Possession"
        }
    },
    "Wide Midfielder, Inverted Winger": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Assists per 90", "xA per 90",
            "Dribbles per 90", "Successful dribbles, %",
            "Fouls suffered per 90", "Shot assists per 90",
            "Passes to penalty area per 90", "Accurate passes to penalty area, %",
            "Deep completions per 90"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Fouls suffered per 90": "Possession",
            "Shot assists per 90": "Possession",
            "Passes to penalty area per 90": "Possession",
            "Accurate passes to penalty area, %": "Possession",
            "Deep completions per 90": "Possession"
        }
    },
    "Wide Midfielder, Defensive Wide Midfielder": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Assists per 90", "xA per 90",
            "Crosses per 90", "Accurate crosses, %", "Dribbles per 90", "Successful dribbles, %",
            "Fouls suffered per 90", "Shot assists per 90",
            "Successful defensive actions per 90", "Defensive duels won, %", "PAdj Interceptions"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Crosses per 90": "Possession",
            "Accurate crosses, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Fouls suffered per 90": "Possession",
            "Shot assists per 90": "Possession",
            "Successful defensive actions per 90": "Defensive",
            "Defensive duels won, %": "Defensive",
            "PAdj Interceptions": "Defensive"
        }
    },

    # ================== STRIKERS ==================
    "Striker, Number 10": {
        "metrics": [
            "Successful defensive actions per 90",
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Assists per 90", "xA per 90", "Shot assists per 90",
            "Forward passes per 90", "Accurate forward passes, %",
            "Passes to final third per 90", "Accurate passes to final third, %",
            "Through passes per 90", "Accurate through passes, %"
        ],
        "groups": {
            "Successful defensive actions per 90": "Off The Ball",
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shot assists per 90": "Attacking",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "Passes to final third per 90": "Possession",
            "Accurate passes to final third, %": "Possession",
            "Through passes per 90": "Possession",
            "Accurate through passes, %": "Possession"
        }
    },
    "Striker, Target Man": {
        "metrics": [
            "Aerial duels per 90", "Aerial duels won, %",
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Head goals per 90", "Assists per 90", "xA per 90", "Shot assists per 90",
            "Offensive duels per 90", "Offensive duels won, %",
            "Passes to penalty area per 90", "Accurate passes to penalty area, %"
        ],
        "groups": {
            "Aerial duels per 90": "Off The Ball",
            "Aerial duels won, %": "Off The Ball",
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Head goals per 90": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shot assists per 90": "Attacking",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "Passes to penalty area per 90": "Possession",
            "Accurate passes to penalty area, %": "Possession"
        }
    },
    "Striker, Penalty Box Striker": {
        "metrics": [
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Shot assists per 90", "Touches in penalty area per 90",
            "Offensive duels per 90", "Offensive duels won, %",
            "Dribbles per 90", "Successful dribbles, %"
        ],
        "groups": {
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Shot assists per 90": "Attacking",
            "Touches in penalty area per 90": "Attacking",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession"
        }
    },
    "Striker, All Round CF": {
        "metrics": [
            "Successful defensive actions per 90", "Aerial duels per 90", "Aerial duels won, %",
            "Non-penalty goals per 90", "xG per 90", "Shots per 90", "Shots on target, %",
            "Goal conversion, %", "Assists per 90", "xA per 90", "Shot assists per 90",
            "Offensive duels per 90", "Offensive duels won, %"
        ],
        "groups": {
            "Successful defensive actions per 90": "Off The Ball",
            "Aerial duels per 90": "Off The Ball",
            "Aerial duels won, %": "Off The Ball",
            "Non-penalty goals per 90": "Attacking",
            "xG per 90": "Attacking",
            "Shots per 90": "Attacking",
            "Shots on target, %": "Attacking",
            "Goal conversion, %": "Attacking",
            "Assists per 90": "Attacking",
            "xA per 90": "Attacking",
            "Shot assists per 90": "Attacking",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession"
        }
    },
    "Striker, Pressing Forward": {
        "metrics": [
            "Successful defensive actions per 90", "Defensive duels per 90", "Defensive duels won, %",
            "Aerial duels per 90", "Aerial duels won, %", "PAdj Interceptions",
            "Offensive duels per 90", "Offensive duels won, %",
            "Dribbles per 90", "Successful dribbles, %",
            "Forward passes per 90", "Accurate forward passes, %",
            "xA per 90", "Shot assists per 90"
        ],
        "groups": {
            "Successful defensive actions per 90": "Off The Ball",
            "Defensive duels per 90": "Off The Ball",
            "Defensive duels won, %": "Off The Ball",
            "Aerial duels per 90": "Off The Ball",
            "Aerial duels won, %": "Off The Ball",
            "PAdj Interceptions": "Off The Ball",
            "Offensive duels per 90": "Possession",
            "Offensive duels won, %": "Possession",
            "Dribbles per 90": "Possession",
            "Successful dribbles, %": "Possession",
            "Forward passes per 90": "Possession",
            "Accurate forward passes, %": "Possession",
            "xA per 90": "Attacking",
            "Shot assists per 90": "Attacking"
        }
    }
}

# Map template -> 6-group so we can gate templates shown per group
TEMPLATE_TO_GROUP = {
    "Goalkeeper": "Goalkeeper",

    "Central Defender, Ball Winning": "Central Defender",
    "Central Defender, Ball Playing": "Central Defender",
    "Central Defender, All Round": "Central Defender",

    "Wide Defender, Full Back": "Wide Defender",
    "Wide Defender, Wing Back": "Wide Defender",
    "Wide Defender, Inverted": "Wide Defender",

    "Central Midfielder, Creative": "Central Midfielder",
    "Central Midfielder, Defensive": "Central Midfielder",
    "Central Midfielder, All Round CM": "Central Midfielder",

    "Wide Midfielder, Touchline Winger": "Wide Midfielder",
    "Wide Midfielder, Inverted Winger": "Wide Midfielder",
    "Wide Midfielder, Defensive Wide Midfielder": "Wide Midfielder",

    "Striker, Number 10": "Central Forward",
    "Striker, Target Man": "Central Forward",
    "Striker, Penalty Box Striker": "Central Forward",
    "Striker, All Round CF": "Central Forward",
    "Striker, Pressing Forward": "Central Forward",
}

# ------------------------ Upload & base dataframe --------------------------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# Normalise helper columns
if "Position" in df.columns:
    df["Positions played"] = df["Position"].astype(str)
else:
    df["Positions played"] = np.nan

df["Six-Group Position"] = df["Position"].apply(map_first_position_to_group) if "Position" in df.columns else np.nan

# ------------------------ Minutes & Age filters ----------------------------
minutes_col = "Minutes played"
min_minutes = st.number_input("Minimum minutes to include", min_value=0, value=800, step=50)
df["_minutes_numeric"] = pd.to_numeric(df.get(minutes_col, np.nan), errors="coerce")
df = df[df["_minutes_numeric"] >= min_minutes].copy()

if "Age" in df.columns:
    df["_age_numeric"] = pd.to_numeric(df["Age"], errors="coerce")
    if df["_age_numeric"].notna().any():
        a_min = int(np.nanmin(df["_age_numeric"]))
        a_max = int(np.nanmax(df["_age_numeric"]))
        sel_age = st.slider("Age range", min_value=a_min, max_value=a_max, value=(a_min, a_max), step=1)
        df = df[df["_age_numeric"].between(sel_age[0], sel_age[1])].copy()

st.caption(f"Filtered by minutes ≥ {min_minutes}. Players remaining, {len(df)}")

# ------------------------ 6-group choice (drives pool) ---------------------
group = st.selectbox("Choose a 6-group position", SIX_GROUPS, index=SIX_GROUPS.index("Central Forward"))
df_group = df[df["Six-Group Position"] == group].copy()
if df_group.empty:
    st.error("No players in this 6-group after filters.")
    st.stop()

# Collapse to one row per player (keep the most-minutes row)
if "Minutes played" in df_group.columns:
    df_group["_minutes_numeric"] = pd.to_numeric(df_group["Minutes played"], errors="coerce")
    df_group.sort_values("_minutes_numeric", ascending=False, inplace=True)
df_group = df_group.drop_duplicates(subset=["Player"], keep="first").copy()

# ------------------------ Template choice (restricted to group) ------------
templates_for_group = [t for t, g in TEMPLATE_TO_GROUP.items() if g == group]
selected_template = st.selectbox("Choose a position template", templates_for_group, index=0)

metrics = position_metrics[selected_template]["metrics"]
metric_groups = position_metrics[selected_template]["groups"]  # <-- needed for shading

# Ensure numeric types (NaN allowed; don't fill zeros before ranking)
for m in metrics:
    if m not in df_group.columns:
        df_group[m] = np.nan
    df_group[m] = pd.to_numeric(df_group[m], errors="coerce")

# ------------------------ Player selectors (from same group) ---------------
players = df_group["Player"].dropna().unique().tolist()
if not players:
    st.error("No players available in this group.")
    st.stop()

if "cmpA" not in st.session_state:
    st.session_state.cmpA = players[0]
if "cmpB" not in st.session_state:
    st.session_state.cmpB = players[1] if len(players) > 1 else None

c1, c2 = st.columns(2)
with c1:
    pA = st.selectbox("Player A", players, index=players.index(st.session_state.cmpA) if st.session_state.cmpA in players else 0, key="cmpA_sel")
    st.session_state.cmpA = pA
with c2:
    pB = st.selectbox("Player B (optional)", ["(none)"] + players, index=(players.index(st.session_state.cmpB) + 1) if st.session_state.cmpB in players else 0, key="cmpB_sel")
    pB = None if pB == "(none)" else pB
    st.session_state.cmpB = pB

# ------------------------ Percentiles within the group ---------------------
LOWER_BETTER = {
    # Add metrics here if lower values should rank higher (will be inverted before ranking)
    # "Conceded goals per 90": True,
}

def compute_percentiles_within_group(metrics_list, group_df):
    bench = group_df.copy()
    for m in metrics_list:
        if m not in bench.columns:
            bench[m] = np.nan
        bench[m] = pd.to_numeric(bench[m], errors="coerce")
        if LOWER_BETTER.get(m, False):
            bench[m] = -bench[m]  # invert so higher is always "better"
    raw = bench[metrics_list].copy()
    pct = (raw.rank(pct=True) * 100.0).round(1)  # pandas ignores NaN in ranking
    return raw, pct

raw_df, pct_df = compute_percentiles_within_group(metrics, df_group)

rowA_pct = pct_df.loc[df_group["Player"] == pA, metrics].iloc[0] if pA in df_group["Player"].values else None
rowB_pct = pct_df.loc[df_group["Player"] == pB, metrics].iloc[0] if (pB and pB in df_group["Player"].values) else None

# ------------------------ Radar (genre background + lines + shaded polygons) ---------------------------
# --- very light, non-clashing background colors for genres ---
GENRE_BG = {
    "Attacking":    "#3b82f6",  # blue-ish
    "Possession":   "#10b981",  # green
    "Defensive":    "#f59e0b",  # orange
    "Off The Ball": "#ef4444",  # red
    "Goalkeeping":  "#8b5cf6",  # purple
}
GENRE_ALPHA = 0.08

def radar_compare(labels, A_vals, B_vals=None, A_name="A", B_name="B",
                  labels_to_genre=None, genre_colors=None, genre_alpha=0.08,
                  show_genre_labels=True, genre_label_radius=112):
    """
    Radar with lightly-shaded genre wedges and HORIZONTAL genre labels placed
    outside the plot so they don't overlap metric labels.
    """
    N = len(labels)
    step = 2 * np.pi / N

# angles and closed polygons
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]
A = A_vals.tolist() + A_vals.tolist()[:1]
B = None
if B_vals is not None:
    B = B_vals.tolist() + B_vals.tolist()[:1]

# figure + polar axes
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))  # was (8.8, 8.8)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# axes / ticks
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=10)

ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80])                 # no tick at 100 -> no outer ring look
ax.set_yticklabels(["20", "40", "60", "80"], fontsize=9)
ax.spines["polar"].set_visible(False)           # hide circular border

# give the plot more breathing room like the other app
plt.subplots_adjust(top=0.90, bottom=0.08, left=0.08, right=0.92)

# ----- Background wedges + HORIZONTAL outside labels -----
if labels_to_genre and genre_colors:
    genre_seq = [labels_to_genre[lbl] for lbl in labels]

    # contiguous runs of same genre around the circle
    runs, run_start = [], 0
    for i in range(1, N):
        if genre_seq[i] != genre_seq[i - 1]:
            runs.append((run_start, i - 1, genre_seq[i - 1]))
            run_start = i
    runs.append((run_start, N - 1, genre_seq[-1]))

    for start_idx, end_idx, g in runs:
        width  = (end_idx - start_idx + 1) * step
        center = start_idx * step + width / 2.0
        color  = genre_colors.get(g, "#999999")

        # wedge fill (stays within 0..100)
        ax.bar([center], [100], width=width, bottom=0,
               color=color, alpha=genre_alpha, edgecolor=None, linewidth=0, zorder=0)

        if show_genre_labels:
            r_lbl = max(120, genre_label_radius)  # place outside the ring
            # horizontal label with small white box for contrast
            ax.text(center, r_lbl, g,
                    rotation=0, rotation_mode="anchor",
                    ha="center", va="center",
                    fontsize=12, fontweight="bold",
                    color=color, zorder=20, clip_on=False,
                    bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=1.5))
    # ----- Player polygons
    ax.plot(angles, A, linewidth=2.5, color="#1f77b4", label=A_name, zorder=10)
    ax.fill(angles, A, color="#1f77b4", alpha=0.20, zorder=10)

    if B is not None:
        ax.plot(angles, B, linewidth=2.5, color="#d62728", label=B_name, zorder=10)
        ax.fill(angles, B, color="#d62728", alpha=0.20, zorder=10)

    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.10))
    plt.tight_layout()
    return fig

# ---------- Build labels & genre mapping ----------
labels_clean = [m.replace(" per 90", "").replace(", %", " (%)") for m in metrics]
metric_groups = position_metrics[selected_template]["groups"]  # {metric: genre}
labels_to_genre = {
    lbl: metric_groups[m] for lbl, m in zip(labels_clean, metrics)
}

# ---------- A/B percentile vectors ----------
A_pct_vals = rowA_pct.values if 'rowA_pct' in locals() and rowA_pct is not None else np.zeros(len(labels_clean))
B_pct_vals = rowB_pct.values if 'rowB_pct' in locals() and rowB_pct is not None else None

# ---------- Title ----------
title_left  = f"<span style='color:#1f77b4; font-weight:700'>{pA}</span>"
title_right = f"<span style='color:#d62728; font-weight:700'>{pB}</span>" if pB else ""
vs_word = " vs " if pB else ""
st.markdown(f"## {title_left}{vs_word}{title_right}", unsafe_allow_html=True)

# ---------- Plot ----------
fig = radar_compare(
    labels=labels_clean,
    A_vals=pd.Series(A_pct_vals),
    B_vals=pd.Series(B_pct_vals) if B_pct_vals is not None else None,
    A_name=pA,
    B_name=pB,
    labels_to_genre=labels_to_genre,
    genre_colors=GENRE_BG,
    genre_alpha=GENRE_ALPHA,
    show_genre_labels=True,
    genre_label_radius=108
)
st.pyplot(fig, use_container_width=True)

# ---------- Diagnostics (optional) ----------
with st.expander("Percentile diagnostics"):
    st.write(f"Pool size (rows after dedupe): {len(df_group)}  |  Unique players: {df_group['Player'].nunique()}")
    d_metric = st.selectbox("Inspect metric", metrics, key="diag_metric")
    s = pd.to_numeric(df_group[d_metric], errors="coerce").dropna().sort_values()
    if not s.empty:
        st.write("Min / Median / Max:", float(s.min()), float(s.median()), float(s.max()))
        def approx_pct(val):
            return round(100.0 * (s <= val).sum() / len(s), 1)
        if pA in df_group["Player"].values:
            vA = float(df_group.loc[df_group["Player"] == pA, d_metric].iloc[0])
            st.write(f"{pA}: raw={vA}, approx percentile≈{approx_pct(vA)}")
        if pB and (pB in df_group["Player"].values):
            vB = float(df_group.loc[df_group["Player"] == pB, d_metric].iloc[0])
            st.write(f"{pB}: raw={vB}, approx percentile≈{approx_pct(vB)}")
