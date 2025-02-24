#!/usr/bin/env python3
"""
Deep Research UI - Interface utilisateur pour le moteur de recherche Gemini
Point d'entrée principal de l'interface utilisateur.
"""

import asyncio
import sys
import traceback

from ui.ui_core import console, THEME
from ui.ui_workflow import run_research_interface


if __name__ == "__main__":
    try:
        asyncio.run(run_research_interface())
    except KeyboardInterrupt:
        console.print("[bold red]Recherche interrompue par l'utilisateur.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Erreur critique: {e}[/bold red]")
        console.print(f"[{THEME['error_color']}]{traceback.format_exc()}[/{THEME['error_color']}]")
        sys.exit(1)