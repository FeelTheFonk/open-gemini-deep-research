"""
Deep Research UI - Interface utilisateur pour le moteur de recherche Gemini
Système MVC complet avec gestionnaire d'état centralisé
"""

from .ui_core import (
    console, PathManager, THEME, TRANSLATION, 
    UIStateManager, state_manager, FileManager, 
    count_nodes, count_knowledge_points, extract_unique_sources
)
from .ui_components import (
    ComponentRegistry, display_welcome_screen, 
    create_main_layout, header_panel, help_panel
)
from .ui_workflow import run_research_interface

# Export public API
__all__ = [
    'run_research_interface',
    'console',
    'state_manager',
    'PathManager',
    'ComponentRegistry',
    'THEME',
    'TRANSLATION',
]

# Version du package
__version__ = '1.0.0'