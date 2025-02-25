"""
Core UI - Configuration, constantes et utilitaires fondamentaux
Implémente le modèle MVC avec gestionnaire d'état centralisé
"""

import os
import json
import datetime
import time
import webbrowser
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union

from dotenv import load_dotenv
from rich.console import Console
from rich.box import HEAVY

# Configuration de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("deep_research")

# Configuration globale
APP_NAME = "LABORATOIRE DE RECHERCHE GEMINI"
APP_VERSION = "1.0.0"

# Chemins d'accès standardisés avec création automatique
class PathManager:
    """Gestionnaire centralisé des chemins d'accès"""
    BASE_DIR = Path("results")
    REPORTS_DIR = BASE_DIR / "reports"
    TREES_DIR = BASE_DIR / "trees"
    GRAPHS_DIR = BASE_DIR / "graphs"
    SUMMARIES_DIR = BASE_DIR / "summaries"
    TEMP_DIR = BASE_DIR / "temp"
    
    @classmethod
    def ensure_all_dirs(cls) -> None:
        """Crée tous les répertoires nécessaires"""
        for attr_name in dir(cls):
            if attr_name.endswith('_DIR') and not attr_name.startswith('__'):
                path = getattr(cls, attr_name)
                if isinstance(path, Path):
                    path.mkdir(exist_ok=True, parents=True)
                    logger.info(f"Répertoire créé/vérifié: {path}")

    @classmethod
    def get_path(cls, dir_type: str, filename: str) -> Path:
        """Récupère un chemin complet correctement formaté"""
        attr_name = f"{dir_type.upper()}_DIR"
        if hasattr(cls, attr_name):
            base_dir = getattr(cls, attr_name)
            return base_dir / filename
        raise ValueError(f"Type de répertoire inconnu: {dir_type}")

# Console Rich unique pour toute l'application
console = Console()

# Couleurs du thème - Regroupées par catégories fonctionnelles
THEME = {
    # Couleurs d'en-tête
    "header_bg": "bright_blue",
    "header_fg": "black",
    "header_border": "bright_blue",
    
    # Couleurs de panneaux
    "panel_border": "cyan",
    "tree_border": "green",
    "dashboard_border": "magenta",
    "stats_border": "yellow",
    "help_border": "bright_blue",
    
    # Couleurs d'état
    "success_color": "bright_green",
    "error_color": "bright_red",
    "warning_color": "bright_yellow",
    "info_color": "bright_cyan",
    "query_color": "bright_magenta",
    
    # Couleurs de statut
    "status_completed": "bright_green",
    "status_in_progress": "bright_yellow",
    "status_waiting": "bright_cyan",
    
    # Style de boîte
    "box_style": HEAVY
}

# Traductions - Système d'internationalisation amélioré
TRANSLATION = {
    # Titres et en-têtes
    "app_title": "LABORATOIRE DE RECHERCHE GEMINI",
    "welcome": "Bienvenue dans votre laboratoire de recherche intelligent",
    
    # Entrées utilisateur
    "enter_query": "Entrez votre requête de recherche",
    "select_mode": "Sélectionnez le mode de recherche",
    "select_breadth": "Largeur de recherche (nombre de requêtes parallèles)",
    "select_depth": "Profondeur de recherche (niveaux d'exploration)",
    
    # Messages de progression
    "generating_questions": "Génération des questions de suivi...",
    "combined_query": "Requête combinée :",
    "launching_research": "Lancement de la recherche approfondie...",
    "research_in_progress": "Recherche en cours...",
    "loading_tree": "Chargement de l'arborescence...",
    
    # Résultats et états
    "no_tree": "Aucune arborescence disponible",
    "research_structure": "Structure de Recherche",
    "dashboard": "Tableau de Bord",
    "stats": "Statistiques",
    "search_status": "État de la Recherche",
    
    # Métriques
    "total_queries": "Requêtes Totales",
    "completed_queries": "Requêtes Complétées",
    "research_depth": "Profondeur Actuelle",
    "elapsed_time": "Temps Écoulé",
    "sources_found": "Sources Trouvées",
    "knowledge_points": "Points de Connaissance",
    "progress_percentage": "Progression: {percent}%",
    
    # Modes d'aide
    "help_mode_fast": "RAPIDE: Recherche superficielle (1-3 min)",
    "help_mode_balanced": "ÉQUILIBRÉ: Compromis vitesse/profondeur (3-6 min)",
    "help_mode_comprehensive": "EXHAUSTIF: Analyse complète, récursive (5-12 min)",
    
    # Génération de rapport
    "generate_report": "Générer le rapport final ?",
    "generating_report": "Génération du rapport final en cours...",
    "report_saved": "Rapport Final enregistré sous :",
    "research_completed": "Recherche terminée sans génération de rapport final",
    "final_report": "Rapport Final",
    "report_browser_opened": "Rapport ouvert dans votre navigateur.",
    
    # Messages d'information
    "follow_up_notice": "Le modèle Gemini a généré et intégré des questions de suivi pour affiner la recherche.",
    "loading": "Chargement...",
    "loading_resources": "Chargement des ressources...",
    
    # Graphiques et visualisations
    "source_network": "Réseau de Sources",
    "knowledge_map": "Carte des Connaissances",
    "generate_graph": "Générer le graphique des connaissances ?",
    "generating_graph": "Génération du graphique de connaissances...",
    "graph_generated": "Graphique généré avec succès",
    "open_graph": "Ouvrir le graphique dans votre navigateur ?",
    "graph_browser_opened": "Graphique ouvert dans votre navigateur.",
    
    # Options utilisateur
    "yes": "Oui",
    "no": "Non",
    "open_report": "Ouvrir le rapport dans votre navigateur ?",
    "export_html": "Exporter en HTML",
    "export_json": "Exporter en JSON",
    "cancel_search": "Annuler la recherche",
    "save_config": "Sauvegarder la configuration",
    "load_config": "Charger une configuration",
    "back_to_home": "Retour à l'accueil",
    "cancel_confirm": "Êtes-vous sûr de vouloir annuler la recherche en cours ?",
    "retry": "Réessayer",
    
    # Messages d'erreur
    "error_occurred": "Une erreur est survenue",
    "error_quota": "Erreur: Ressource épuisée. Veuillez vérifier votre quota Gemini.",
    "error_questions": "Erreur lors de la génération des questions de suivi",
    "error_report": "Erreur lors de la génération du rapport final"
}

# Gestionnaire d'état centralisé (pattern Singleton)
class UIStateManager:
    """Gestionnaire d'état centralisé de l'interface utilisateur"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIStateManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialise l'état par défaut"""
        self.tree_data = {}
        self.visited_urls = {}
        self.start_time = time.time()
        self.is_searching = False
        self.current_mode = "balanced"
        self.current_query = ""
        self.breadth = 10
        self.depth = 5
        self.learnings = []
        self.report_path = None
        self.graph_path = None
        self.notifications = []
        self.debug_mode = False
        
    def reset(self):
        """Réinitialise l'état complet"""
        self._initialize()
        
    def update_tree(self, tree_data: Dict[str, Any]) -> None:
        """Met à jour l'arbre de recherche"""
        self.tree_data = tree_data
        self._save_tree_snapshot()
        
    def update_urls(self, urls: Dict[str, Any]) -> None:
        """Met à jour les URLs visitées"""
        self.visited_urls = urls
        
    def add_learning(self, learning: str) -> None:
        """Ajoute un nouvel apprentissage"""
        if learning not in self.learnings:
            self.learnings.append(learning)
    
    def add_notification(self, message: str, level: str = "info") -> None:
        """Ajoute une notification avec niveau"""
        self.notifications.append({
            "message": message,
            "level": level,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def get_elapsed_time(self) -> float:
        """Retourne le temps écoulé depuis le début"""
        return time.time() - self.start_time
    
    def _save_tree_snapshot(self) -> None:
        """Sauvegarde un instantané de l'arbre pour mise à jour en direct"""
        try:
            with open("research_tree.json", "w", encoding="utf-8") as f:
                json.dump(self.tree_data, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'instantané: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Calcule et retourne les statistiques courantes"""
        total, completed = count_nodes(self.tree_data)
        knowledge_points = count_knowledge_points(self.tree_data)
        sources_count = extract_unique_sources(self.visited_urls)
        
        return {
            "total_queries": total,
            "completed_queries": completed,
            "completion_rate": (completed / total) if total > 0 else 0,
            "current_depth": self.tree_data.get("depth", 0),
            "knowledge_points": knowledge_points,
            "sources_count": sources_count,
            "elapsed_time": format_elapsed_time(self.get_elapsed_time())
        }

# Instanciation du gestionnaire d'état
state_manager = UIStateManager()

# Classe gestionnaire de fichiers
class FileManager:
    """Gestionnaire centralisé des opérations de fichiers"""
    
    @staticmethod
    def save_json(data: Any, filename: str, subfolder: str) -> Optional[str]:
        """Sauvegarde des données JSON avec gestion d'erreurs améliorée"""
        path = PathManager.get_path(subfolder, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Fichier JSON sauvegardé: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde JSON: {e}")
            console.print(f"[{THEME['error_color']}]Erreur lors de la sauvegarde JSON: {e}[/{THEME['error_color']}]")
            return None

    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Charge un fichier JSON avec gestion d'erreurs"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Fichier JSON chargé: {filepath}")
            return data
        except FileNotFoundError:
            logger.warning(f"Fichier non trouvé: {filepath}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Format JSON invalide: {filepath}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors du chargement JSON: {e}")
            console.print(f"[{THEME['error_color']}]Erreur lors du chargement JSON: {e}[/{THEME['error_color']}]")
            return None

    @staticmethod
    def save_markdown(report: str, query: str) -> Optional[str]:
        """Sauvegarde le rapport markdown avec formatage du nom de fichier"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = sanitize_filename(query, max_length=50)
        filename = f"report_{safe_query}_{timestamp}.md"
        path = PathManager.get_path("reports", filename)
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Rapport Markdown sauvegardé: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            console.print(f"[{THEME['error_color']}]Erreur lors de la sauvegarde du rapport: {e}[/{THEME['error_color']}]")
            return None

    @staticmethod
    def open_file(path: Union[str, Path]) -> bool:
        """Ouvre un fichier avec l'application par défaut du système"""
        try:
            path_obj = Path(path) if isinstance(path, str) else path
            if path_obj.exists():
                webbrowser.open(f"file://{path_obj.absolute()}")
                logger.info(f"Fichier ouvert dans le navigateur: {path}")
                return True
            logger.warning(f"Fichier non trouvé pour ouverture: {path}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture du fichier: {e}")
            console.print(f"[{THEME['error_color']}]Erreur lors de l'ouverture du fichier: {e}[/{THEME['error_color']}]")
            return False

# Fonctions utilitaires optimisées
def format_elapsed_time(seconds: float) -> str:
    """Formate le temps écoulé en heures, minutes, secondes"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def sanitize_filename(text: str, max_length: int = 50) -> str:
    """Crée un nom de fichier sécurisé à partir d'un texte"""
    if not text:
        return "unnamed"
    # Filtrer les caractères autorisés et remplacer les espaces
    safe_text = "".join(c for c in text if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    # Tronquer si nécessaire
    if len(safe_text) > max_length:
        return safe_text[:max_length] + "..."
    return safe_text

def count_nodes(node: Optional[Dict[str, Any]]) -> Tuple[int, int]:
    """Compte le nombre total de nœuds et de nœuds complétés (optimisé)"""
    if not node:
        return 0, 0
        
    # Version itérative pour éviter la récursion profonde
    total, completed = 0, 0
    queue = [node]
    
    while queue:
        current = queue.pop(0)
        if not current:
            continue
            
        total += 1
        if current.get("status") == "completed":
            completed += 1
            
        queue.extend(current.get("sub_queries", []))
        
    return total, completed

def count_knowledge_points(node: Optional[Dict[str, Any]]) -> int:
    """Compte le nombre total de points de connaissance (optimisé)"""
    if not node:
        return 0
    
    # Version itérative
    total = 0
    queue = [node]
    
    while queue:
        current = queue.pop(0)
        if not current:
            continue
            
        total += len(current.get("learnings", []))
        queue.extend(current.get("sub_queries", []))
        
    return total

def extract_unique_sources(visited_urls: Optional[Dict[str, Any]]) -> int:
    """Extrait le nombre de sources uniques"""
    if not visited_urls:
        return 0
    return len(visited_urls)

# Réexportation des fonctions et classes pour backward compatibility
save_json = FileManager.save_json
load_json = FileManager.load_json
save_markdown = FileManager.save_markdown
open_file = FileManager.open_file
ensure_dirs = PathManager.ensure_all_dirs