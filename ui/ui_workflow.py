"""
UI Workflow - Logique principale du workflow de recherche
"""

import os
import json
import asyncio
import datetime
import time
import traceback
from pathlib import Path

from dotenv import load_dotenv
from rich.prompt import Prompt, Confirm
from rich.console import Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from google.api_core.exceptions import ResourceExhausted

from src.deep_research import DeepSearch
from .ui_core import (
    console, ensure_dirs, THEME, TRANSLATION, save_json, save_markdown, 
    format_elapsed_time, open_file, extract_unique_sources
)
from .ui_components import (
    header_panel, help_panel, display_tree, display_dashboard, 
    create_main_layout, follow_up_notice, display_welcome_screen, 
    display_error_panel, animated_loading
)
from .ui_visualizers import (
    export_html, generate_knowledge_graph, export_research_summary
)


async def show_splash_screen():
    """Affiche un écran de démarrage animé"""
    # Texte du logo ASCII
    logo = """
 .d8888b.  8888888888        d8888 8888888b.   .d8888b.  888    888 
d88P       888              d88888 888   Y88b d88P  Y88b 888    888 
Y88b.      888             d88P888 888    888 888    888 888    888 
 "Y888b.   8888888        d88P 888 888   d88P 888        8888888888 
    "Y88b. 888           d88P  888 8888888P"  888        888    888 
      "888 888          d88P   888 888 T88b   888    888 888    888 
Y88b  d88P 888         d8888888888 888  T88b  Y88b  d88P 888    888 
 "Y8888P"  8888888888 d88P     888 888   T88b  "Y8888P"  888    888 
                                                                    
                                                                    
                                                                    
    888                       d8888               888888b.                  
    888                      d88888               888  "88b                 
    888                     d88P888               888  .88P                 
    888                    d88P 888               8888888K.                 
    888                   d88P  888               888  "Y88b                
    888                  d88P   888               888    888                
    888                 d8888888888               888   d88P                
    88888888           d88P     888               8888888P"
    """
    
    # Couleurs pour l'animation
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    
    # Animation du logo
    for i in range(6):
        console.clear()
        colored_logo = f"[bold {colors[i]}]{logo}[/]"
        console.print(colored_logo)
        console.print(f"\n[bold white]Laboratoire de Recherche Avancée[/]")
        console.print(f"[dim]v1.0.0 | Initialisation...[/]")
        
        # Points de progression
        dots = "." * (i % 4)
        console.print(f"\n[bold cyan]Démarrage{dots.ljust(3)}[/]")
        
        await asyncio.sleep(0.3)
    
    console.clear()


async def ask_follow_up_questions(ds, initial_query):
    """Interface améliorée pour les questions de suivi"""
    try:
        console.print(Panel(
            f"[{THEME['info_color']}]{TRANSLATION['generating_questions']}[/{THEME['info_color']}]",
            border_style=THEME['info_color'],
            box=THEME['box_style']
        ))
        
        follow_up_questions = ds.generate_follow_up_questions(initial_query)
    except Exception as e:
        console.print(Panel(
            f"[{THEME['error_color']}]{TRANSLATION['error_questions']}: {e}[/{THEME['error_color']}]",
            border_style=THEME['error_color'],
            box=THEME['box_style']
        ))
        return []
    
    # Afficher un en-tête pour les questions
    if follow_up_questions:
        console.print(Text(f"\n{TRANSLATION['generating_questions']}", style=f"bold {THEME['info_color']}"))
    
    answers = []
    for i, question in enumerate(follow_up_questions, 1):
        # Afficher le numéro de la question
        formatted_question = f"[{i}/{len(follow_up_questions)}] {question}"
        answer = Prompt.ask(f"[bold {THEME['query_color']}]{formatted_question}[/]")
        answers.append({"question": question, "answer": answer})
    
    return answers


def combine_query(initial_query, follow_ups):
    """Combine la requête initiale avec les questions de suivi"""
    qa_text = "\n".join([f"- {item['question']}: {item['answer']}" for item in follow_ups])
    combined = f"Initial query: {initial_query}\n\nFollow up Q&A:\n{qa_text}"
    return combined


async def run_research(ds, query, breadth, depth):
    """Exécution de la recherche avec suivi de progression via le fichier research_tree.json"""
    console.print(f"[{THEME['info_color']}]{TRANSLATION['launching_research']}[/{THEME['info_color']}]")
    
    start_time = time.time()
    
    # Configuration de la mise en page
    layout = create_main_layout()
    layout["header"].update(header_panel())
    layout["sidebar"].update(help_panel())
    
    # Fonction de suivi des mises à jour
    async def update_display():
        while True:
            try:
                # Lire l'arbre de recherche actuel s'il existe
                try:
                    with open("research_tree.json", "r", encoding="utf-8") as f:
                        tree_data = json.load(f)
                    
                    # Mettre à jour la visualisation de l'arbre
                    layout["tree"].update(display_tree(tree_data))
                    
                    # Mettre à jour le tableau de bord
                    layout["dashboard"].update(display_dashboard(tree_data, {}, start_time))
                    
                    # Mettre à jour la barre de progression
                    progress_text = Text(TRANSLATION['research_in_progress'], style=f"bold {THEME['info_color']}")
                    layout["progress"].update(Panel(
                        progress_text,
                        border_style=THEME['info_color'],
                        box=THEME['box_style']
                    ))
                    
                except FileNotFoundError:
                    # Fichier tree.json pas encore créé, afficher un message d'attente
                    loading_text = Text(TRANSLATION['loading_tree'], style=f"bold {THEME['warning_color']}")
                    layout["tree"].update(Panel(
                        loading_text,
                        title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
                        border_style=THEME['tree_border'],
                        box=THEME['box_style']
                    ))
                except json.JSONDecodeError:
                    # Fichier tree.json potentiellement en cours d'écriture
                    loading_text = Text(TRANSLATION['loading_tree'], style=f"bold {THEME['warning_color']}")
                    layout["tree"].update(Panel(
                        loading_text,
                        title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
                        border_style=THEME['tree_border'],
                        box=THEME['box_style']
                    ))
            except Exception as e:
                # Éviter que des erreurs d'affichage interrompent la recherche
                error_text = Text(f"Erreur d'affichage: {e}", style=f"bold {THEME['error_color']}")
                layout["progress"].update(Panel(
                    error_text,
                    border_style=THEME['error_color'],
                    box=THEME['box_style']
                ))
            
            # Attendre avant la prochaine mise à jour
            await asyncio.sleep(2)
    
    # Exécuter la recherche avec mise à jour en temps réel
    with Live(layout, refresh_per_second=4):
        # Lancer la tâche de mise à jour en arrière-plan
        update_task = asyncio.create_task(update_display())
        
        try:
            # Exécuter la recherche
            result = await ds.deep_research(query, breadth, depth, learnings=[], visited_urls={})
            
            # Ajouter un délai pour afficher la fin
            await asyncio.sleep(1)
            
            # Nettoyer
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass
            
            return result
        except Exception as e:
            # Nettoyer en cas d'erreur
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass
            
            console.print(f"[{THEME['error_color']}]Erreur pendant la recherche: {e}[/{THEME['error_color']}]")
            console.print(traceback.format_exc())
            return {"learnings": [], "visited_urls": {}}


async def process_final_report(ds, combined_query, result, tree_data, start_time):
    """Traiter et afficher le rapport final"""
    learnings = result.get("learnings", [])
    visited_urls = result.get("visited_urls", {})
    end_time = time.time()
    
    # Calculer les statistiques finales
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Demander si l'utilisateur souhaite générer un rapport final
    generate_report = Confirm.ask(
        f"[{THEME['info_color']}]{TRANSLATION['generate_report']}[/{THEME['info_color']}]",
        default=True
    )
    
    if generate_report:
        try:
            console.print(Panel(
                f"[{THEME['success_color']}]{TRANSLATION['generating_report']}[/{THEME['success_color']}]",
                border_style=THEME['info_color'],
                box=THEME['box_style']
            ))
            
            report = ds.generate_final_report(combined_query, learnings, visited_urls)
            
            # Afficher un aperçu du rapport
            md_report = Markdown(report[:2000] + "... [suite du rapport]" if len(report) > 2000 else report)
            console.print(Panel(
                md_report,
                title=f"[bold {THEME['success_color']}]{TRANSLATION['final_report']}[/bold {THEME['success_color']}]",
                border_style=THEME['success_color'],
                box=THEME['box_style']
            ))
            
            # Sauvegarder le rapport
            report_path = save_markdown(report, combined_query.split("\n")[0])
            if report_path:
                console.print(Panel(
                    f"[{THEME['success_color']}]{TRANSLATION['report_saved']}[/{THEME['success_color']}]\n{report_path}",
                    border_style=THEME['success_color'],
                    box=THEME['box_style']
                ))
                
                # Exporter en HTML et ouvrir dans le navigateur
                open_html = Confirm.ask(
                    f"[{THEME['info_color']}]{TRANSLATION['open_report']}[/{THEME['info_color']}]",
                    default=True
                )
                
                if open_html:
                    html_path = export_html(report_path, combined_query.split("\n")[0])
                    if html_path:
                        open_file(html_path)
                        # Utiliser Text au lieu de f-string pour éviter les problèmes de formatage
                        success_msg = Text(TRANSLATION["report_browser_opened"])
                        success_msg.stylize(f"bold {THEME['success_color']}")
                        console.print(success_msg)
            
            # Exporter un résumé de recherche complet
            export_research_summary(
                tree_data, 
                visited_urls, 
                combined_query.split("\n")[0], 
                learnings, 
                start_time, 
                end_time
            )
            
            # Générer et visualiser le graphique de connaissances
            generate_graph = Confirm.ask(
                f"[{THEME['info_color']}]{TRANSLATION['generate_graph']}[/{THEME['info_color']}]",
                default=True
            )
            
            if generate_graph:
                console.print(Panel(
                    f"[{THEME['info_color']}]{TRANSLATION['generating_graph']}[/{THEME['info_color']}]",
                    border_style=THEME['info_color'],
                    box=THEME['box_style']
                ))
                
                # Générer le graphique
                graph_path = generate_knowledge_graph(tree_data, visited_urls)
                
                if graph_path:
                    console.print(f"[{THEME['success_color']}]{TRANSLATION['graph_generated']}: {graph_path}[/{THEME['success_color']}]")
                    
                    # Demander s'il faut ouvrir le graphique dans le navigateur
                    open_graph = Confirm.ask(
                        f"[{THEME['info_color']}]{TRANSLATION['open_graph']}[/{THEME['info_color']}]",
                        default=True
                    )
                    
                    if open_graph:
                        open_file(graph_path)
                        # Utiliser Text au lieu de f-string pour éviter les problèmes de formatage
                        success_msg = Text(TRANSLATION["graph_browser_opened"])
                        success_msg.stylize(f"bold {THEME['success_color']}")
                        console.print(success_msg)
            
        except ResourceExhausted as e:
            console.print(Panel(
                f"[{THEME['error_color']}]{TRANSLATION['error_quota']}\n{e}[/{THEME['error_color']}]",
                border_style=THEME['error_color'],
                box=THEME['box_style']
            ))
        except Exception as e:
            console.print(Panel(
                f"[{THEME['error_color']}]{TRANSLATION['error_report']}: {e}[/{THEME['error_color']}]",
                border_style=THEME['error_color'],
                box=THEME['box_style']
            ))
            console.print(traceback.format_exc())
    else:
        console.print(Panel(
            f"[{THEME['info_color']}]{TRANSLATION['research_completed']}[/{THEME['info_color']}]",
            border_style=THEME['info_color'],
            box=THEME['box_style']
        ))
    
    # Retourner les informations du rapport
    return {
        "report_path": report_path if generate_report else None,
        "duration": {
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": elapsed_time
        }
    }


async def run_research_interface():
    """Interface principale du laboratoire de recherche"""
    # Initialisation
    ensure_dirs()
    load_dotenv()
    
    # Afficher l'écran de démarrage
    await show_splash_screen()
    
    try:
        # Afficher l'écran de bienvenue
        display_welcome_screen()
        
        # Collecter les informations pour la recherche
        initial_query = Prompt.ask(f"[bold {THEME['query_color']}]{TRANSLATION['enter_query']}[/]")
        mode = Prompt.ask(
            f"[bold {THEME['info_color']}]{TRANSLATION['select_mode']}[/]",
            choices=["fast", "balanced", "comprehensive"],
            default="comprehensive"
        )
        breadth = int(Prompt.ask(
            f"[bold {THEME['info_color']}]{TRANSLATION['select_breadth']}[/]",
            default="10"
        ))
        depth = int(Prompt.ask(
            f"[bold {THEME['info_color']}]{TRANSLATION['select_depth']}[/]",
            default="5"
        ))
        
        # Initialiser DeepSearch
        ds = DeepSearch(api_key=os.getenv("GEMINI_KEY"), mode=mode)
        
        # Marquer le début de la recherche
        start_time = time.time()
        
        # Générer et poser des questions de suivi
        follow_up_answers = await ask_follow_up_questions(ds, initial_query)
        
        # Combiner la requête avec les questions de suivi
        if follow_up_answers:
            combined_query = combine_query(initial_query, follow_up_answers)
            console.print(Panel(
                f"[{THEME['info_color']}]{TRANSLATION['combined_query']}\n{combined_query}[/{THEME['info_color']}]",
                border_style=THEME['info_color'],
                box=THEME['box_style']
            ))
        else:
            combined_query = initial_query
        
        # Lancer la recherche
        result = await run_research(ds, combined_query, breadth, depth)
        
        # Lire l'arbre final
        try:
            with open("research_tree.json", "r", encoding="utf-8") as f:
                tree_data = json.load(f)
        except Exception:
            tree_data = {}
        
        # Afficher les résultats de la recherche
        console.clear()
        results_layout = Layout()
        results_layout.split_row(
            Layout(display_tree(tree_data), name="tree", ratio=3),
            Layout(display_dashboard(tree_data, result.get("visited_urls", {}), start_time), name="dashboard", ratio=2)
        )
        
        console.print(results_layout)
        
        # Notification pour les questions de suivi
        follow_up_notice(mode)
        
        # Enregistrer l'arbre de recherche
        if tree_data:
            save_json(tree_data, f"research_tree_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "trees")
        
        # Traiter et générer le rapport final
        await process_final_report(ds, combined_query, result, tree_data, start_time)
        
    except KeyboardInterrupt:
        console.print("[bold red]Recherche interrompue par l'utilisateur.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Erreur inattendue: {e}[/bold red]")
        console.print(traceback.format_exc())