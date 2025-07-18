"""
Professional GUI Styling for PandaDOCK
Modern design system with consistent colors, typography, and animations
"""

MAIN_COLORS = {
    'primary': '#6366f1',
    'primary_dark': '#4f46e5',
    'primary_light': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'background': '#ffffff',
    'surface': '#f8fafc',
    'text': '#1e293b',
    'text_secondary': '#64748b',
    'border': '#e2e8f0',
    'shadow': 'rgba(0, 0, 0, 0.1)'
}

PROFESSIONAL_THEME = f"""
QMainWindow {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['background']}, stop: 1 {MAIN_COLORS['surface']});
    color: {MAIN_COLORS['text']};
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}}

QPushButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
    color: white !important;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    border-radius: 10px;
    padding: 12px 20px;
    margin: 2px;
    border: 2px solid {MAIN_COLORS['primary_dark']};
    min-height: 40px;
    min-width: 180px;
    box-shadow: 0 2px 4px -1px {MAIN_COLORS['shadow']};
}}

QPushButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 #5b56f0, stop: 1 #4338ca);
    color: white !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.25);
}}

QPushButton:pressed {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 #4338ca, stop: 1 #3730a3);
    color: white !important;
    transform: translateY(0px);
    box-shadow: 0 1px 2px -1px rgba(0, 0, 0, 0.2);
}}

QPushButton:disabled {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['surface']}, stop: 1 #e2e8f0);
    color: {MAIN_COLORS['text']} !important;
    border: 1px solid {MAIN_COLORS['border']};
    opacity: 0.7;
    box-shadow: none;
}}

QProgressBar {{
    border: 1px solid {MAIN_COLORS['border']};
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 12px;
    color: {MAIN_COLORS['text']};
    background-color: {MAIN_COLORS['surface']};
    height: 20px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']});
    border-radius: 6px;
    margin: 2px;
}}

/* Additional button styling for maximum specificity and visibility */
QWidget QPushButton {{
    color: white !important;
}}


QWidget QPushButton:disabled {{
    color: {MAIN_COLORS['text']} !important;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['surface']}, stop: 1 #e2e8f0) !important;
    border: 1px solid {MAIN_COLORS['border']} !important;
}}

QPushButton:focus {{
    color: white !important;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']}) !important;
    border: 2px solid {MAIN_COLORS['primary_light']} !important;
    outline: none;
}}

QWidget QPushButton:enabled {{
    color: white !important;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']}) !important;
    border: 2px solid {MAIN_COLORS['primary_dark']} !important;
}}

QWidget QPushButton:enabled:!disabled {{
    color: white !important;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']}) !important;
    border: 2px solid {MAIN_COLORS['primary_dark']} !important;
}}

/* Specific styling for enabled button by object name */
QPushButton#enabledButton {{
    color: white !important;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 {MAIN_COLORS['primary']}, stop: 1 {MAIN_COLORS['primary_dark']}) !important;
    border: 2px solid {MAIN_COLORS['primary_dark']} !important;
    font-weight: 600;
}}
"""

LOADING_ANIMATION_STYLE = """
QLabel#loadingLabel {
    color: #6366f1;
    font-size: 14px;
    font-weight: 600;
    padding: 10px;
}
"""

def get_loading_spinner_html():
    """Returns HTML for a CSS loading spinner"""
    return '''
    <div style="display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div style="
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </div>
    '''