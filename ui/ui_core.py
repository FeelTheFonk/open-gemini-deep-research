"""
Core UI - Configuration, constantes et utilitaires fondamentaux
"""

import os
import json
import datetime
import time
import webbrowser
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.box import HEAVY

# Configuration globale
APP_NAME = "LABORATOIRE DE RECHERCHE GEMINI"
APP_VERSION = "1.0.0"

# Chemins d'accès 
BASE_DIR = Path("results")
REPORTS_DIR = BASE_DIR / "reports"
TREES_DIR = BASE_DIR / "trees"
GRAPHS_DIR = BASE_DIR / "graphs"

# Console Rich
console = Console()

# Couleurs du thème
THEME = {
    "header_bg": "bright_blue",
    "header_fg": "black",
    "header_border": "bright_blue",
    "panel_border": "cyan",
    "tree_border": "green",
    "dashboard_border": "magenta",
    "stats_border": "yellow",
    "help_border": "bright_blue",
    "success_color": "bright_green",
    "error_color": "bright_red",
    "warning_color": "bright_yellow",
    "info_color": "bright_cyan",
    "query_color": "bright_magenta",
    "status_completed": "bright_green",
    "status_in_progress": "bright_yellow",
    "status_waiting": "bright_cyan",
    "box_style": HEAVY
}

# Traductions
TRANSLATION = {
    "app_title": "LABORATOIRE DE RECHERCHE GEMINI",
    "welcome": "Bienvenue dans votre laboratoire de recherche intelligent",
    "enter_query": "Entrez votre requête de recherche",
    "select_mode": "Sélectionnez le mode de recherche",
    "select_breadth": "Largeur de recherche (nombre de requêtes parallèles)",
    "select_depth": "Profondeur de recherche (niveaux d'exploration)",
    "generating_questions": "Génération des questions de suivi...",
    "combined_query": "Requête combinée :",
    "launching_research": "Lancement de la recherche approfondie...",
    "research_in_progress": "Recherche en cours...",
    "no_tree": "Aucune arborescence disponible",
    "generate_report": "Générer le rapport final ?",
    "generating_report": "Génération du rapport final en cours...",
    "report_saved": "Rapport Final enregistré sous :",
    "research_completed": "Recherche terminée sans génération de rapport final",
    "error_quota": "Erreur: Ressource épuisée. Veuillez vérifier votre quota Gemini.",
    "error_questions": "Erreur lors de la génération des questions de suivi",
    "error_report": "Erreur lors de la génération du rapport final",
    "research_structure": "Structure de Recherche",
    "dashboard": "Tableau de Bord",
    "stats": "Statistiques",
    "total_queries": "Requêtes Totales",
    "completed_queries": "Requêtes Complétées",
    "research_depth": "Profondeur Actuelle",
    "elapsed_time": "Temps Écoulé",
    "sources_found": "Sources Trouvées",
    "knowledge_points": "Points de Connaissance",
    "help_mode_fast": "RAPIDE: Recherche superficielle (1-3 min)",
    "help_mode_balanced": "ÉQUILIBRÉ: Compromis vitesse/profondeur (3-6 min)",
    "help_mode_comprehensive": "EXHAUSTIF: Analyse complète, récursive (5-12 min)",
    "yes": "Oui",
    "no": "Non",
    "open_report": "Ouvrir le rapport dans votre navigateur ?",
    "follow_up_notice": "Le modèle Gemini a généré et intégré des questions de suivi pour affiner la recherche.",
    "final_report": "Rapport Final",
    "source_network": "Réseau de Sources",
    "knowledge_map": "Carte des Connaissances",
    "loading": "Chargement...",
    "export_html": "Exporter en HTML",
    "export_json": "Exporter en JSON",
    "search_status": "État de la Recherche",
    "generate_graph": "Générer le graphique des connaissances ?",
    "generating_graph": "Génération du graphique de connaissances...",
    "graph_generated": "Graphique généré avec succès",
    "open_graph": "Ouvrir le graphique dans votre navigateur ?",
    "report_browser_opened": "Rapport ouvert dans votre navigateur.",
    "graph_browser_opened": "Graphique ouvert dans votre navigateur.",
    "progress_percentage": "Progression: {percent}%",
    "cancel_search": "Annuler la recherche",
    "save_config": "Sauvegarder la configuration",
    "load_config": "Charger une configuration",
    "back_to_home": "Retour à l'accueil",
    "error_occurred": "Une erreur est survenue",
    "retry": "Réessayer",
    "loading_tree": "Chargement de l'arborescence...",
    "cancel_confirm": "Êtes-vous sûr de vouloir annuler la recherche en cours ?",
    "loading_resources": "Chargement des ressources..."
}

# Fonctions utilitaires
def ensure_dirs():
    """Crée tous les répertoires nécessaires"""
    for folder in [BASE_DIR, REPORTS_DIR, TREES_DIR, GRAPHS_DIR]:
        folder.mkdir(exist_ok=True, parents=True)

def format_elapsed_time(seconds):
    """Formate le temps écoulé en heures, minutes, secondes"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def save_json(data, filename, subfolder):
    """Sauvegarde des données JSON avec gestion d'erreurs améliorée"""
    path = BASE_DIR / subfolder / filename
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de la sauvegarde JSON: {e}[/{THEME['error_color']}]")
        return None

def load_json(filepath):
    """Charge un fichier JSON avec gestion d'erreurs"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors du chargement JSON: {e}[/{THEME['error_color']}]")
        return None

def save_markdown(report, query):
    """Sauvegarde le rapport markdown avec formatage du nom de fichier"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c for c in query if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    # Limiter la longueur du nom de fichier
    safe_query = safe_query[:50] + "..." if len(safe_query) > 50 else safe_query
    filename = f"report_{safe_query}_{timestamp}.md"
    path = REPORTS_DIR / filename
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        return str(path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de la sauvegarde du rapport: {e}[/{THEME['error_color']}]")
        return None

def sanitize_filename(text, max_length=50):
    """Crée un nom de fichier sécurisé à partir d'un texte"""
    safe_text = "".join(c for c in text if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    return safe_text[:max_length] + "..." if len(safe_text) > max_length else safe_text

def open_file(path):
    """Ouvre un fichier avec l'application par défaut du système"""
    try:
        if os.path.exists(path):
            webbrowser.open(f"file://{os.path.abspath(path)}")
            return True
        return False
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de l'ouverture du fichier: {e}[/{THEME['error_color']}]")
        return False

def count_nodes(node):
    """Compte le nombre total de nœuds et de nœuds complétés"""
    if not node:
        return 0, 0
    total = 1
    completed = 1 if node.get("status") == "completed" else 0
    for child in node.get("sub_queries", []):
        t, c = count_nodes(child)
        total += t
        completed += c
    return total, completed

def count_knowledge_points(node):
    """Compte le nombre total de points de connaissance"""
    if not node:
        return 0
    total = len(node.get("learnings", []))
    for child in node.get("sub_queries", []):
        total += count_knowledge_points(child)
    return total

def extract_unique_sources(visited_urls):
    """Extrait le nombre de sources uniques"""
    if not visited_urls:
        return 0
    return len(visited_urls)