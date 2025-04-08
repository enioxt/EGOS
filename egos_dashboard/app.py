"""
EGOS Monitoring Dashboard - Main Application
Displays system status, metrics, and integrates with the MYCELIUM message bus.
"""

# Import from our modular structure
from src.config import PAGE_CONFIG
from src.koios_logger import KoiosLogger
from src.nats_client import connect_to_nats
from src.theming import apply_theme
from src.translations import _
from src.ui_components import (
    render_atlas_expander,
    render_coruja_expander,
    render_cronos_expander,
    render_ethik_expander,
    render_harmony_expander,
    render_koios_expander,
    render_mycelium_expander,
    render_nats_connect_button,
    render_nexus_expander,
    render_overview_metrics,
    render_page_header,
    render_sidebar,
    render_subsystem_status_table,
    render_system_health_visualization,
)
import streamlit as st

# Setup logger
logger = KoiosLogger.get_logger("DASHBOARD.Main")

# --- Page Configuration ---
st.set_page_config(
    page_title=str(PAGE_CONFIG["page_title"]),
    page_icon=str(PAGE_CONFIG["page_icon"]),
    layout=str(PAGE_CONFIG["layout"]),
    initial_sidebar_state=str(PAGE_CONFIG["initial_sidebar_state"]),
    menu_items=PAGE_CONFIG["menu_items"],
)

# --- Initialize Session State ---
# Default language
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Default theme
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # Default theme

# NATS connection status
if "nats_connection_status" not in st.session_state:
    st.session_state.nats_connection_status = _("nats_status_disconnected")


# --- Theme Toggle ---
def change_theme():
    """Handle theme toggle."""
    new_theme = "dark" if st.session_state.theme_toggle else "light"
    st.session_state.theme = new_theme

    # Log theme change
    KoiosLogger.log_user_action(logger, "theme_change", {"new_theme": new_theme})


# --- Apply Theme CSS ---
st.markdown(apply_theme(st.session_state.theme), unsafe_allow_html=True)


# --- NATS Connection Handler ---
def nats_connect_handler():
    """Handle NATS connection button click."""
    connect_to_nats()
    # Force a rerun to update the UI with the new status
    st.rerun()


# --- Main UI Layout ---
# Theme toggle in sidebar
is_dark_theme = st.session_state.theme == "dark"
st.sidebar.toggle(
    "🌙 Dark Mode",
    key="theme_toggle",
    value=is_dark_theme,
    on_change=change_theme,
    help="Switch between light and dark themes",
)

# Render page header
render_page_header()

# Render sidebar and get selected subsystem
selected_subsystem = render_sidebar()

# Log subsystem selection
if (
    "previous_subsystem" not in st.session_state
    or st.session_state.get("previous_subsystem") != selected_subsystem
):
    st.session_state.previous_subsystem = selected_subsystem
    KoiosLogger.log_user_action(
        logger, "subsystem_selection", {"selected_subsystem": selected_subsystem}
    )

# Connect to NATS button
render_nats_connect_button()

# Process button click for NATS connection
if st.session_state.get("connect_nats_button"):
    # Run the connection handler
    nats_connect_handler()
    # Reset the button state
    st.session_state["connect_nats_button"] = False

# --- Content based on selected subsystem ---
if selected_subsystem == "Overview":
    # Overview section
    render_overview_metrics()
    render_subsystem_status_table()
    render_system_health_visualization()

    # Subsystem details (collapsed by default)
    render_ethik_expander()
    render_koios_expander()
    render_coruja_expander()
    render_mycelium_expander()
    render_atlas_expander()
    render_nexus_expander()
    render_cronos_expander()
    render_harmony_expander()

elif selected_subsystem == "ETHIK":
    # ETHIK-focused page
    st.header("⚖️ ETHIK - Ethical Guardian")
    render_ethik_expander()

elif selected_subsystem == "KOIOS":
    # KOIOS-focused page
    st.header("📚 KOIOS - Standards & Knowledge")
    render_koios_expander()

elif selected_subsystem == "CORUJA":
    # CORUJA-focused page
    st.header("🦉 CORUJA - AI Orchestration")
    render_coruja_expander()

elif selected_subsystem == "MYCELIUM":
    # MYCELIUM-focused page
    st.header("🍄 MYCELIUM - Communication Network")
    render_mycelium_expander()

elif selected_subsystem == "ATLAS":
    # ATLAS-focused page
    st.header("🗺️ ATLAS - System Cartographer")
    render_atlas_expander()

elif selected_subsystem == "NEXUS":
    # NEXUS-focused page
    st.header("⚙️ NEXUS - Modular Analysis")
    render_nexus_expander()

elif selected_subsystem == "CRONOS":
    # CRONOS-focused page
    st.header("⏱️ CRONOS - Time & History")
    render_cronos_expander()

elif selected_subsystem == "HARMONY":
    # HARMONY-focused page
    st.header("🔄 HARMONY - Integration & Compatibility")
    render_harmony_expander()

# Log application startup
KoiosLogger.log_system_event(
    logger,
    "application_startup",
    "EGOS Dashboard started successfully",
    {"initial_subsystem": selected_subsystem},
)
