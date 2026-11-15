import streamlit as st
import html
from datetime import date
from supabase import create_client, Client

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="RankUp | JEE Prep Portal",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "theme_mode": "Dark",
    "access_token": None,
    "refresh_token": None,
    "user": None,
    "answers": {},
    "quiz_submitted": False,
    "study_hours": 6.0,
    "flash_message": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SUPABASE CONNECTION
# =========================================================
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"].strip(),
        st.secrets["SUPABASE_KEY"].strip()
    )


try:
    supabase = get_supabase_client()
except Exception as e:
    st.error("Supabase connection could not be initialized.")
    st.caption(str(e))
    st.stop()


# =========================================================
# RESTORE AUTH SESSION
# =========================================================
if st.session_state.access_token and st.session_state.refresh_token:
    try:
        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        response = supabase.auth.get_user()
        st.session_state.user = response.user

        current_session = supabase.auth.get_session()

        if current_session:
            st.session_state.access_token = current_session.access_token
            st.session_state.refresh_token = current_session.refresh_token

    except Exception:
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None


# =========================================================
# THEME
# =========================================================
theme = st.session_state.theme_mode

if theme == "Dark":
    page_bg = "#090d1b"
    panel_bg = "#171f3b"
    sidebar_bg = "#10162a"
    text_color = "#eef1ff"
    muted_color = "#98a7cf"
    border_color = "#29365c"
    metric_bg = "linear-gradient(145deg,#171f3b,#11182d)"
else:
    page_bg = "#f4f6fc"
    panel_bg = "#ffffff"
    sidebar_bg = "#e9edfa"
    text_color = "#17213d"
    muted_color = "#5c6885"
    border_color = "#d8def0"
