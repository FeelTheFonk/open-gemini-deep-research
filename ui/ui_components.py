"""
UI Components - Composants d'interface réutilisables pour l'application
Implémente le pattern de conception Component pour une interface modulaire
"""

import asyncio
import datetime
import time
from typing import Dict, Any, List, Optional, Callable

from rich.console import Group
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn

from .ui_core import (
    THEME, TRANSLATION, console, state_manager,
    count_nodes, count_knowledge_points, extract_unique_sources, format_elapsed_time
)


class ComponentRegistry:
    """Registre centralisé des composants UI"""
    _components = {}
    
    @classmethod
    def register(cls, name: str):
        """Enregistre un composant pour utilisation ultérieure"""
        def decorator(component_factory: Callable):
            cls._components[name] = component_factory
            return component_factory
        return decorator
    
    @classmethod
    def get(cls, name: str, **kwargs) -> Any:
        """Récupère une instance du composant par son nom"""
        if name in cls._components:
            return cls._components[name](**kwargs)
        raise ValueError(f"Composant non enregistré: {name}")


@ComponentRegistry.register("header")
def header_panel():
    """Crée un panneau d'en-tête stylisé"""
    # Version et date
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    version_text = f"v1.0.0 | {now}"
    
    # Créer le titre stylisé
    title = Text(TRANSLATION["app_title"], style=f"bold {THEME['header_fg']} on {THEME['header_bg']}")
    title.justify = "center"
    
    # Ajouter une note de bienvenue
    welcome = Text(f"\n{TRANSLATION['welcome']}", style="italic")
    welcome.justify = "center"
    
    # Ajouter la version en bas
    footer = Text(f"\n{version_text}", style="dim")
    footer.justify = "right"
    
    # Assembler le contenu
    header_content = Group(title, welcome, footer)
    
    return Panel(
        header_content,
        border_style=THEME['header_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )


@ComponentRegistry.register("help")
def help_panel():
    """Crée un panneau d'aide contextuelle"""
    # Infos sur les modes de recherche
    modes_table = Table(box=None, show_header=False, padding=(0, 1))
    modes_table.add_column("Mode", style=f"bold {THEME['info_color']}")
    modes_table.add_column("Description", style="white")
    
    modes_table.add_row("⚡", TRANSLATION['help_mode_fast'])
    modes_table.add_row("⚖️", TRANSLATION['help_mode_balanced'])
    modes_table.add_row("🔍", TRANSLATION['help_mode_comprehensive'])
    
    # Assembler le contenu d'aide
    help_content = Group(modes_table)
    
    return Panel(
        help_content,
        title="Aide & Information",
        border_style=THEME['help_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )


def build_tree(node: Optional[Dict[str, Any]]) -> Tree:
    """Construit un arbre de recherche visuel avec couleurs thématiques (optimisé)"""
    if not node:
        return Tree(f"[{THEME['warning_color']}]{TRANSLATION['no_tree']}[/{THEME['warning_color']}]")
    
    # Utiliser une approche itérative au lieu de récursive
    query = node.get('query', TRANSLATION['loading'])
    status = node.get('status', 'waiting')
    
    # Sélectionner la couleur en fonction du statut
    if status == 'completed':
        status_color = THEME['status_completed']
    elif status == 'in_progress':
        status_color = THEME['status_in_progress']
    else:
        status_color = THEME['status_waiting']
    
    # Créer le nœud racine
    root_tree = Tree(f"[bold {THEME['query_color']}]{query}[/] - [{status_color}]{status}[/]")
    
    # Utiliser une file pour l'approche itérative
    queue = [(node, root_tree)]
    
    while queue:
        current_node, parent_tree = queue.pop(0)
        
        for child in current_node.get("sub_queries", []):
            child_query = child.get('query', TRANSLATION['loading'])
            child_status = child.get('status', 'waiting')
            
            # Déterminer la couleur du statut de l'enfant
            if child_status == 'completed':
                child_status_color = THEME['status_completed']
            elif child_status == 'in_progress':
                child_status_color = THEME['status_in_progress']
            else:
                child_status_color = THEME['status_waiting']
            
            # Ajouter le nœud enfant avec formatage
            branch = parent_tree.add(f"[{THEME['info_color']}]{child_query}[/] - [{child_status_color}]{child_status}[/]")
            
            # Ajouter cet enfant à la file pour traitement ultérieur
            queue.append((child, branch))
    
    return root_tree


@ComponentRegistry.register("tree")
def display_tree(tree_data: Optional[Dict[str, Any]]) -> Panel:
    """Affiche l'arbre de recherche dans un panneau stylisé"""
    if not tree_data:
        return Panel(
            f"[{THEME['warning_color']}]{TRANSLATION['no_tree']}[/{THEME['warning_color']}]",
            title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
            border_style=THEME['tree_border'],
            box=THEME['box_style']
        )
    
    tree = build_tree(tree_data)
    return Panel(
        tree,
        title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
        border_style=THEME['tree_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )


@ComponentRegistry.register("dashboard")
def display_dashboard(tree_data: Optional[Dict[str, Any]] = None, visited_urls: Optional[Dict[str, Any]] = None, start_time: Optional[float] = None) -> Panel:
    """Affiche un tableau de bord complet avec statistiques"""
    # Utiliser les données du gestionnaire d'état si non fournies
    tree_data = tree_data or state_manager.tree_data
    visited_urls = visited_urls or state_manager.visited_urls
    start_time = start_time or state_manager.start_time
    
    if not tree_data:
        return Panel(
            f"[{THEME['warning_color']}]{TRANSLATION['no_tree']}[/{THEME['warning_color']}]",
            title=f"[bold {THEME['info_color']}]{TRANSLATION['dashboard']}[/]",
            border_style=THEME['dashboard_border'],
            box=THEME['box_style']
        )
    
    total, completed = count_nodes(tree_data)
    knowledge_points = count_knowledge_points(tree_data)
    current_depth = tree_data.get("depth", 0)
    sources_count = extract_unique_sources(visited_urls)
    elapsed = format_elapsed_time(time.time() - start_time)
    
    # Créer un tableau de statistiques
    stats_table = Table(box=THEME['box_style'], show_header=False, padding=(0, 1))
    stats_table.add_column("Metric", style=f"bold {THEME['info_color']}")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row(TRANSLATION['total_queries'], str(total))
    completion_percentage = completed * 100 // total if total > 0 else 0
    stats_table.add_row(TRANSLATION['completed_queries'], f"{completed} ({completion_percentage}%)")
    stats_table.add_row(TRANSLATION['research_depth'], str(current_depth))
    stats_table.add_row(TRANSLATION['sources_found'], str(sources_count))
    stats_table.add_row(TRANSLATION['knowledge_points'], str(knowledge_points))
    stats_table.add_row(TRANSLATION['elapsed_time'], elapsed)
    
    # Calcul du ratio de progression
    progress_ratio = completed / total if total > 0 else 0
    
    # Barre de progression visuelle avec blocs unicode
    progress_blocks = int(progress_ratio * 20)
    progress_bar = "█" * progress_blocks + "░" * (20 - progress_blocks)
    progress_text = Text(f"{progress_bar} {progress_ratio * 100:.1f}%")
    
    # État de la recherche
    if completed == total and total > 0:
        status = Text(f"✓ {TRANSLATION['search_status']}: ", style=THEME['success_color'])
        status.append("COMPLÉTÉ", style=f"bold {THEME['success_color']}")
    else:
        status = Text(f"⟳ {TRANSLATION['search_status']}: ", style=THEME['warning_color'])
        status.append("EN COURS", style=f"bold {THEME['warning_color']}")
    
    # Assembler les composants
    dashboard_content = Group(
        stats_table,
        Text(""),  # Espacement
        status,
        Text(""),  # Espacement
        progress_text
    )
    
    return Panel(
        dashboard_content,
        title=f"[bold {THEME['info_color']}]{TRANSLATION['dashboard']}[/]",
        border_style=THEME['dashboard_border'],
        box=THEME['box_style']
    )


@ComponentRegistry.register("progress_bar")
def create_research_progress_bar():
    """Crée une barre de progression avancée pour la recherche"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TaskProgressColumn(),
        expand=True
    )


@ComponentRegistry.register("main_layout")
def create_main_layout():
    """Crée la mise en page principale de l'application"""
    layout = Layout()
    
    # Division principale : en-tête et contenu principal
    layout.split_column(
        Layout(name="header", size=6),
        Layout(name="main")
    )
    
    # Division du contenu principal : zone principale et zone d'aide
    layout["main"].split_row(
        Layout(name="content", ratio=3),
        Layout(name="sidebar", ratio=1)
    )
    
    # Sous-divisions de la zone de contenu
    layout["content"].split_column(
        Layout(name="progress", size=3),
        Layout(name="results")
    )
    
    # Sous-division de la zone de résultats
    layout["results"].split_row(
        Layout(name="tree", ratio=3),
        Layout(name="dashboard", ratio=2)
    )
    
    return layout


@ComponentRegistry.register("follow_up_notice")
def follow_up_notice(mode: str):
    """Affiche une notification sur les questions de suivi générées par Gemini"""
    if mode == "comprehensive":
        notice = Text(TRANSLATION["follow_up_notice"], style=f"bold {THEME['warning_color']}")
        console.print(Panel(
            Align.center(notice),
            border_style=THEME['warning_color'],
            box=THEME['box_style']
        ))


@ComponentRegistry.register("welcome_screen")
def display_welcome_screen():
    """Affiche l'écran de bienvenue avec animation"""
    console.clear()
    console.print(ComponentRegistry.get("header"))
    console.print(Panel(
        Align.center(Text(
            "\n🔍 Prêt à explorer l'univers de l'information\n\n"
            "Posez votre question et laissez Gemini Deep Research\n"
            "transformer vos requêtes en connaissances approfondies.\n\n"
            "L'intelligence artificielle au service de votre curiosité.\n",
            justify="center"
        )),
        title="[bold]Explorateur de Connaissances[/bold]",
        border_style=THEME['info_color'],
        box=THEME['box_style'],
        padding=(1, 2)
    ))


@ComponentRegistry.register("error_panel")
def display_error_panel(error_message: str, error_details: Optional[str] = None):
    """Affiche un panneau d'erreur avec détails"""
    error_content = Text(error_message, style=f"bold {THEME['error_color']}")
    
    if error_details:
        details = Text(f"\n{error_details}", style="dim")
        content = Group(error_content, details)
    else:
        content = error_content
    
    return Panel(
        content,
        title=f"[bold {THEME['error_color']}]{TRANSLATION['error_occurred']}[/]",
        border_style=THEME['error_color'],
        box=THEME['box_style'],
        padding=(1, 2)
    )


class LoadingAnimation:
    """Classe pour gérer les animations de chargement avec contrôle avancé"""
    def __init__(self, message: str, spinner_chars: str = "|/-\\"):
        self.message = message
        self.spinner_chars = spinner_chars
        self.is_running = False
        self.task = None
    
    async def _animate(self):
        """Animation interne de chargement"""
        i = 0
        while self.is_running:
            console.print(f"{self.spinner_chars[i % len(self.spinner_chars)]} {self.message}", end="\r")
            i += 1
            await asyncio.sleep(0.1)
    
    async def start(self, duration: Optional[float] = None):
        """Démarre l'animation avec durée optionnelle"""
        self.is_running = True
        self.task = asyncio.create_task(self._animate())
        
        if duration is not None:
            await asyncio.sleep(duration)
            await self.stop()
    
    async def stop(self):
        """Arrête proprement l'animation"""
        if self.is_running:
            self.is_running = False
            if self.task:
                await asyncio.wait_for(self.task, timeout=0.5)
            console.print(" " * (len(self.message) + 2), end="\r")  # Effacer la ligne


@ComponentRegistry.register("loading_animation")
async def animated_loading(message: str, duration: float = 3):
    """Fonction wrapper pour l'animation de chargement"""
    animation = LoadingAnimation(message)
    await animation.start(duration)