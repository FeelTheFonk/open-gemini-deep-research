"""
Deep Research UI - Interface utilisateur pour le moteur de recherche Gemini
"""

from .ui_core import console, ensure_dirs, THEME, TRANSLATION
from .ui_workflow import run_research_interface

__all__ = ['run_research_interface']