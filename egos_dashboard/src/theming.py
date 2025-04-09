"""
Theme configuration for the EGOS Dashboard.
Applies custom themes for light and dark modes using Streamlit's theming capabilities.
Aligned with the EGOS website color palette to ensure a consistent brand experience.
"""

# Website color values from docs/css/base/_variables.css
EGOS_COLORS = {
    "primary": "#081e36",  # Darker Deep Blue (--primary-color)
    "accent": "#FF6600",   # Warm Orange (--accent-color)
    "background": "#f8f9fa", # Very light grey (--background-color)
    "surface": "#ffffff",   # White for cards/surfaces (--surface-color)
    "text": "#333",        # Dark grey for text (--text-color)
    "text_light": "#666",  # Lighter grey text (--text-light)
    "text_on_primary": "#ffffff", # White text on dark blue
    "text_on_accent": "#ffffff",  # White text on orange
    "border": "#e0e0e0",   # Light border color
    "shadow": "rgba(0, 0, 0, 0.08)", # Softer shadow
    "hover_shadow": "rgba(0, 0, 0, 0.12)" # Hover shadow
}

# Light theme aligned with website colors
LIGHT_THEME = f"""
<style>
    /* Base styles */
    .stApp {{
        background-color: {EGOS_COLORS["background"]};
        color: {EGOS_COLORS["text"]};
    }}
    
    /* Main elements */
    .stTabs [data-baseweb="tab-panel"] {{
        background-color: {EGOS_COLORS["surface"]};
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {EGOS_COLORS["surface"]};
        border-right: 1px solid {EGOS_COLORS["border"]};
    }}
    
    /* Buttons and interactive elements */
    .stButton>button, .stDownloadButton>button {{
        background-color: {EGOS_COLORS["accent"]};
        color: {EGOS_COLORS["text_on_accent"]};
        border: none;
    }}
    
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: {EGOS_COLORS["accent"]}e0;
    }}
    
    /* Cards and containers */
    div[data-testid="stExpander"] {{
        border: 1px solid {EGOS_COLORS["border"]};
        border-radius: 8px;
        background-color: {EGOS_COLORS["surface"]};
        box-shadow: 0 2px 5px {EGOS_COLORS["shadow"]};
    }}

    /* Headers */
    h1, h2, h3 {{
        color: {EGOS_COLORS["primary"]};
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-weight: bold;
        color: {EGOS_COLORS["primary"]};
    }}
    
    /* Font adjustments */
    .stApp, .stTextInput>div>div>input {{
        font-family: 'Inter', sans-serif;
    }}
</style>
"""

# Dark theme based on the primary and accent colors from the website
DARK_THEME = f"""
<style>
    /* Base styles */
    .stApp {{
        background-color: #0c1425; /* Darker version of primary color */
        color: #e0e0e0;
    }}
    
    /* Main elements */
    .stTabs [data-baseweb="tab-panel"] {{
        background-color: #121d2f; /* Slightly lighter than background */
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #081e36; /* Primary color */
        border-right: 1px solid #1a2c45;
    }}
    
    /* Buttons and interactive elements */
    .stButton>button, .stDownloadButton>button {{
        background-color: {EGOS_COLORS["accent"]};
        color: {EGOS_COLORS["text_on_accent"]};
        border: none;
    }}
    
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: {EGOS_COLORS["accent"]}e0;
    }}
    
    /* Cards and containers */
    div[data-testid="stExpander"] {{
        border: 1px solid #1a2c45;
        border-radius: 8px;
        background-color: #121d2f;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }}

    /* Headers */
    h1, h2, h3 {{
        color: #e0e0e0;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-weight: bold;
        color: #ffffff;
    }}
    
    /* Font adjustments */
    .stApp, .stTextInput>div>div>input {{
        font-family: 'Inter', sans-serif;
    }}
</style>
"""


def apply_theme(theme_name: str) -> str:
    """
    Returns the CSS string for the selected theme.

    Args:
        theme_name: 'light' or 'dark'

    Returns:
        CSS string to apply the theme.
    """
    if theme_name == "light":
        return LIGHT_THEME
    else:
        return DARK_THEME
