"""
UI Components - Composants d'interface réutilisables pour l'application
"""

import asyncio
import datetime
import time

from rich.console import Group
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn

from .ui_core import THEME, TRANSLATION, console, count_nodes, count_knowledge_points, extract_unique_sources, format_elapsed_time


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
    help_content = Group(
        modes_table
    )
    
    return Panel(
        help_content,
        title="Aide & Information",
        border_style=THEME['help_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )


def build_tree(node):
    """Construit un arbre de recherche visuel avec couleurs thématiques"""
    if not node:
        return Tree(f"[{THEME['warning_color']}]{TRANSLATION['no_tree']}[/{THEME['warning_color']}]")
        
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
    tree = Tree(f"[bold {THEME['query_color']}]{query}[/] - [{status_color}]{status}[/]")
    
    def add_nodes(n, parent):
        for child in n.get("sub_queries", []):
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
            branch = parent.add(f"[{THEME['info_color']}]{child_query}[/] - [{child_status_color}]{child_status}[/]")
            
            # Ajouter récursivement les enfants de ce nœud
            add_nodes(child, branch)
    
    # Ajouter tous les nœuds enfants
    add_nodes(node, tree)
    return tree


def display_tree(tree_data):
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


def display_dashboard(tree_data, visited_urls, start_time):
    """Affiche un tableau de bord complet avec statistiques"""
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
    stats_table.add_row(TRANSLATION['completed_queries'], f"{completed} ({completed * 100 // total if total > 0 else 0}%)")
    stats_table.add_row(TRANSLATION['research_depth'], str(current_depth))
    stats_table.add_row(TRANSLATION['sources_found'], str(sources_count))
    stats_table.add_row(TRANSLATION['knowledge_points'], str(knowledge_points))
    stats_table.add_row(TRANSLATION['elapsed_time'], elapsed)
    
    # Calcul du ratio de progression
    progress_ratio = completed / total if total > 0 else 0
    
    # Barre de progression visuelle
    progress_bar = "█" * int(progress_ratio * 20) + "░" * (20 - int(progress_ratio * 20))
    progress_text = Text(f"{progress_bar} {progress_ratio * 100:.1f}%")
    
    # État de la recherche
    if completed == total:
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


def follow_up_notice(mode):
    """Affiche une notification sur les questions de suivi générées par Gemini"""
    if mode == "comprehensive":
        notice = Text(TRANSLATION["follow_up_notice"], style=f"bold {THEME['warning_color']}")
        console.print(Panel(
            Align.center(notice),
            border_style=THEME['warning_color'],
            box=THEME['box_style']
        ))


def display_welcome_screen():
    """Affiche l'écran de bienvenue avec animation"""
    console.clear()
    console.print(header_panel())
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


def display_error_panel(error_message, error_details=None):
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


async def animated_loading(message, duration=3):
    """Affiche un message de chargement animé"""
    spinner = "|/-\\"
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        console.print(f"{spinner[i % len(spinner)]} {message}", end="\r")
        i += 1
        await asyncio.sleep(0.1)
    
    console.print(" " * (len(message) + 2), end="\r")  # Effacer la ligne