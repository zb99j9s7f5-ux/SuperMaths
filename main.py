import streamlit as st
from dotenv import load_dotenv
from auth import show_auth
from baseline import show_baseline
from dashboard import show_dashboard
from assignments import show_assignment
from level_test import show_level_test
from practice import show_practice
from landing import show_landing
import extra_streamlit_components as stx
import os

load_dotenv("api.env")

st.set_page_config(page_title="SuperMaths", page_icon="🧮", layout="wide")

st.markdown("""
    <style>
        iframe[title="extra_streamlit_components.CookieManager.cookie_manager"] {
            display: none !important;
        }
        #MainMenu, footer, header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

cookie_manager = stx.CookieManager()

defaults = {
    "logged_in": False, "username": None, "active_assignment": None,
    "show_baseline": False, "show_level_test": False,
    "practice_topic": None, "practice_grade": None, "show_landing": True,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if not st.session_state.logged_in:
    saved_user = cookie_manager.get("supermaths_user")
    if saved_user:
        st.session_state.logged_in = True
        st.session_state.username = saved_user
        st.session_state.show_landing = False

if st.session_state.show_landing and not st.session_state.logged_in:
    show_landing()
elif not st.session_state.logged_in:
    show_auth(cookie_manager)
elif st.session_state.show_baseline:
    show_baseline()
elif st.session_state.show_level_test:
    show_level_test()
elif st.session_state.practice_topic:
    show_practice()
elif st.session_state.active_assignment:
    show_assignment(st.session_state.active_assignment)
else:
    show_dashboard(cookie_manager)