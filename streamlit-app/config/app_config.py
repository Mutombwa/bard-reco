"""
Application Configuration
========================
Central configuration for the BARD-RECO application
"""

import os
from pathlib import Path

# Application information
APP_NAME = "BARD-RECO"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Modern Cloud-Based Reconciliation System"

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
EXPORTS_DIR = DATA_DIR / 'exports'
REPORTS_DIR = DATA_DIR / 'reports'
UPLOADS_DIR = DATA_DIR / 'uploads'

# Create directories if they don't exist
for dir_path in [DATA_DIR, EXPORTS_DIR, REPORTS_DIR, UPLOADS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Reconciliation settings
RECONCILIATION_CONFIG = {
    'default_fuzzy_threshold': 85,
    'default_date_tolerance': 3,
    'default_amount_tolerance': 0.1,
    'enable_ai': True,
    'max_file_size_mb': 100,
    'supported_file_types': ['xlsx', 'xls', 'csv'],
}

# Authentication settings
AUTH_CONFIG = {
    'session_timeout_minutes': 120,
    'password_min_length': 6,
    'enable_registration': True,
}

# UI settings
UI_CONFIG = {
    'theme': 'light',
    'page_icon': '💼',
    'layout': 'wide',
    'items_per_page': 100,
}

# Export settings
EXPORT_CONFIG = {
    'default_format': 'xlsx',
    'include_summary': True,
    'include_charts': True,
}

# Application configuration dictionary
APP_CONFIG = {
    'app': {
        'name': APP_NAME,
        'version': APP_VERSION,
        'description': APP_DESCRIPTION,
    },
    'paths': {
        'base': BASE_DIR,
        'data': DATA_DIR,
        'exports': EXPORTS_DIR,
        'reports': REPORTS_DIR,
        'uploads': UPLOADS_DIR,
    },
    'reconciliation': RECONCILIATION_CONFIG,
    'auth': AUTH_CONFIG,
    'ui': UI_CONFIG,
    'export': EXPORT_CONFIG,
}
