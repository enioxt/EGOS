"""
Theme configuration for the EGOS Dashboard.
Applies custom themes for light and dark modes using Streamlit's theming capabilities.
"""

LIGHT_THEME = """
[theme]
primaryColor="#6A0DAD" # Vibrant purple
backgroundColor="#F0F2F6" # Light grey background
secondaryBackgroundColor="#FFFFFF" # White for cards/elements
textColor="#1E1E1E" # Dark grey text for better contrast
font="sans serif"
"""

DARK_THEME = """
[theme]
primaryColor="#9370DB" # Lighter purple for dark mode
backgroundColor="#0E1117" # Default dark background
secondaryBackgroundColor="#262730" # Slightly lighter dark for cards
textColor="#FAFAFA" # Light text
font="sans serif"
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
