#!/usr/bin/env python3
"""
Deep Research UI - Interface utilisateur pour le moteur de recherche Gemini
Point d'entrée principal de l'interface utilisateur.
"""

import asyncio
import sys
import traceback
import logging
from argparse import ArgumentParser

from ui.ui_core import console, THEME, PathManager, logger
from ui.ui_workflow import run_research_interface


def parse_arguments():
    """Parse les arguments de la ligne de commande"""
    parser = ArgumentParser(description="Interface de recherche avancée Gemini")
    parser.add_argument("--debug", action="store_true", help="Activer le mode debug")
    parser.add_argument("--clean", action="store_true", help="Nettoyer les fichiers temporaires avant exécution")
    return parser.parse_args()


def configure_logging(debug_mode=False):
    """Configure le niveau de logging selon le mode"""
    level = logging.DEBUG if debug_mode else logging.INFO
    logger.setLevel(level)
    logging.getLogger("deep_research").setLevel(level)


async def main():
    """Fonction principale asynchrone"""
    args = parse_arguments()
    
    # Configurer le logging
    configure_logging(args.debug)
    
    # Valider l'environnement
    try:
        # Assurer l'existence des répertoires
        PathManager.ensure_all_dirs()
        
        # Nettoyer les fichiers temporaires si demandé
        if args.clean:
            import shutil
            import os
            
            # Nettoyer le fichier temporaire research_tree.json
            if os.path.exists("research_tree.json"):
                os.remove("research_tree.json")
                logger.info("Fichier temporaire research_tree.json supprimé")
        
        # Exécuter l'interface de recherche
        await run_research_interface()
        
    except KeyboardInterrupt:
        console.print(f"[bold {THEME['error_color']}]Recherche interrompue par l'utilisateur.[/bold {THEME['error_color']}]")
    except Exception as e:
        console.print(f"[bold {THEME['error_color']}]Erreur critique: {e}[/bold {THEME['error_color']}]")
        console.print(f"[{THEME['error_color']}]{traceback.format_exc()}[/{THEME['error_color']}]")
        logger.error(f"Erreur critique: {e}\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[bold {THEME['error_color']}]Erreur fatale: {e}[/bold {THEME['error_color']}]")
        logger.critical(f"Erreur fatale: {e}\n{traceback.format_exc()}")
        sys.exit(1)