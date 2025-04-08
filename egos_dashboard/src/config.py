"""
Configuration settings for the EGOS Dashboard.
Contains constants, page configuration, and environment-specific settings.
"""

# --- NATS Connection Settings ---
NATS_SERVER_URL = "nats://localhost:4222"  # Default local NATS server URL

# --- Page Configuration Settings ---
PAGE_CONFIG = {
    "page_title": "EGOS Monitoring Dashboard",
    "page_icon": "☸️",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        "Get Help": "https://github.com/enioxt/EGOS/issues",  # Assuming public repo now
        "Report a bug": "https://github.com/enioxt/EGOS/issues",  # Assuming public repo now
        "About": """
        # EGOS - Evolutionary Gnostic Operating System

        **Version:** 0.1.0 (Dashboard)
        **GitHub:** https://github.com/enioxt/EGOS # Assuming public repo now

        Monitoring dashboard for the EGOS AI ecosystem.
        Built with Ethics, Modularity, Beauty, and Unconditional Love.
        """,
    },
}

# --- GitHub Repository Settings ---
BASE_GITHUB_URL = "https://github.com/enioxt/EGOS/tree/main/subsystems"
