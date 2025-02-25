"""
UI Workflow - Logique principale du workflow de recherche
Implémente le contrôleur MVC pour coordonner l'interface utilisateur
"""

import os
import json
import asyncio
import datetime
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union, Callable

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
    console, logger, THEME, TRANSLATION, state_manager,
    PathManager, FileManager
)
from .ui_components import (
    ComponentRegistry, LoadingAnimation
)
from .ui_visualizers import (
    export_html, generate_knowledge_graph, export_research_summary
)


class DeepResearchController:
    """Contrôleur principal pour l'orchestration du workflow de recherche"""
    
    def __init__(self):
        """Initialisation du contrôleur"""
        self.ds = None
        self.api_key = os.getenv("GEMINI_KEY")
        self.layout = None
        self.update_task = None
        
    async def initialize(self):
        """Initialisation asynchrone des ressources"""
        # Assurer que tous les répertoires existent
        PathManager.ensure_all_dirs()
        
        # Charger les variables d'environnement
        load_dotenv()
        
        # Vérifier la clé API
        if not self.api_key:
            logger.error("Clé API Gemini manquante dans les variables d'environnement")
            console.print(Panel(
                f"[{THEME['error_color']}]Erreur: Clé API Gemini non configurée. "
                f"Veuillez définir la variable d'environnement GEMINI_KEY.[/{THEME['error_color']}]",
                border_style=THEME['error_color'],
                box=THEME['box_style']
            ))
            return False
            
        # Initialiser le gestionnaire d'état
        state_manager.reset()
        
        return True
        
    async def show_splash_screen(self):
        """Affiche un écran de démarrage animé optimisé"""
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
        
        # Utiliser une animation plus efficace avec timer
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        
        for i in range(6):
            console.clear()
            console.print(f"[bold {colors[i]}]{logo}[/]")
            console.print(f"\n[bold white]Laboratoire de Recherche Avancée[/]")
            console.print(f"[dim]v1.0.0 | Initialisation...[/]")
            
            # Points de progression
            dots = "." * (i % 4)
            console.print(f"\n[bold cyan]Démarrage{dots.ljust(3)}[/]")
            
            await asyncio.sleep(0.3)
        
        console.clear()
    
    async def ask_follow_up_questions(self, initial_query: str) -> List[Dict[str, str]]:
        """Interface améliorée pour les questions de suivi"""
        try:
            console.print(Panel(
                f"[{THEME['info_color']}]{TRANSLATION['generating_questions']}[/{THEME['info_color']}]",
                border_style=THEME['info_color'],
                box=THEME['box_style']
            ))
            
            follow_up_questions = self.ds.generate_follow_up_questions(initial_query)
            
            # Utilisation d'une liste compréhension et validation
            if not follow_up_questions:
                logger.warning("Aucune question de suivi générée")
                return []
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération des questions de suivi: {str(e)}")
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
        # Utiliser enumerate pour des indices 1-based
        for i, question in enumerate(follow_up_questions, 1):
            # Afficher le numéro de la question
            formatted_question = f"[{i}/{len(follow_up_questions)}] {question}"
            answer = Prompt.ask(f"[bold {THEME['query_color']}]{formatted_question}[/]")
            answers.append({"question": question, "answer": answer})
        
        return answers
    
    def combine_query(self, initial_query: str, follow_ups: List[Dict[str, str]]) -> str:
        """Combine la requête initiale avec les questions de suivi"""
        if not follow_ups:
            return initial_query
            
        qa_text = "\n".join([f"- {item['question']}: {item['answer']}" for item in follow_ups])
        combined = f"Initial query: {initial_query}\n\nFollow up Q&A:\n{qa_text}"
        return combined
    
    async def update_display(self):
        """Fonction asynchrone de mise à jour de l'affichage"""
        try:
            while True:
                try:
                    # Lire l'arbre de recherche actuel s'il existe
                    try:
                        with open("research_tree.json", "r", encoding="utf-8") as f:
                            tree_data = json.load(f)
                        
                        # Mettre à jour le gestionnaire d'état
                        state_manager.update_tree(tree_data)
                        
                        # Mettre à jour la visualisation de l'arbre
                        self.layout["tree"].update(ComponentRegistry.get("tree", tree_data=tree_data))
                        
                        # Mettre à jour le tableau de bord
                        self.layout["dashboard"].update(ComponentRegistry.get("dashboard", 
                                                                         tree_data=tree_data, 
                                                                         visited_urls=state_manager.visited_urls, 
                                                                         start_time=state_manager.start_time))
                        
                        # Mettre à jour la barre de progression
                        progress_text = Text(TRANSLATION['research_in_progress'], style=f"bold {THEME['info_color']}")
                        self.layout["progress"].update(Panel(
                            progress_text,
                            border_style=THEME['info_color'],
                            box=THEME['box_style']
                        ))
                        
                    except FileNotFoundError:
                        # Fichier tree.json pas encore créé, afficher un message d'attente
                        loading_text = Text(TRANSLATION['loading_tree'], style=f"bold {THEME['warning_color']}")
                        self.layout["tree"].update(Panel(
                            loading_text,
                            title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
                            border_style=THEME['tree_border'],
                            box=THEME['box_style']
                        ))
                    except json.JSONDecodeError:
                        # Fichier tree.json potentiellement en cours d'écriture
                        loading_text = Text(TRANSLATION['loading_tree'], style=f"bold {THEME['warning_color']}")
                        self.layout["tree"].update(Panel(
                            loading_text,
                            title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
                            border_style=THEME['tree_border'],
                            box=THEME['box_style']
                        ))
                        
                except Exception as e:
                    # Éviter que des erreurs d'affichage interrompent la recherche
                    error_msg = f"Erreur d'affichage: {e}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    error_text = Text(error_msg, style=f"bold {THEME['error_color']}")
                    self.layout["progress"].update(Panel(
                        error_text,
                        border_style=THEME['error_color'],
                        box=THEME['box_style']
                    ))
                
                # Attendre avant la prochaine mise à jour (avec backoff exponentiel si erreurs)
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            # Capture propre des annulations de tâche
            logger.info("Tâche de mise à jour affichage annulée")
            
    async def run_research(self, query: str, breadth: int, depth: int) -> Dict[str, Any]:
        """Exécution de la recherche avec suivi de progression via le fichier research_tree.json"""
        console.print(f"[{THEME['info_color']}]{TRANSLATION['launching_research']}[/{THEME['info_color']}]")
        
        # Initialiser le temps de départ dans le gestionnaire d'état
        state_manager.start_time = time.time()
        state_manager.is_searching = True
        state_manager.current_query = query
        state_manager.breadth = breadth
        state_manager.depth = depth
        
        # Configuration de la mise en page
        self.layout = ComponentRegistry.get("main_layout")
        self.layout["header"].update(ComponentRegistry.get("header"))
        self.layout["sidebar"].update(ComponentRegistry.get("help"))
        
        # Exécuter la recherche avec mise à jour en temps réel
        with Live(self.layout, refresh_per_second=4):
            # Lancer la tâche de mise à jour en arrière-plan
            self.update_task = asyncio.create_task(self.update_display())
            
            try:
                # Exécuter la recherche
                result = await self.ds.deep_research(query, breadth, depth, learnings=[], visited_urls={})
                
                # Mettre à jour l'état
                state_manager.update_urls(result.get("visited_urls", {}))
                state_manager.learnings = result.get("learnings", [])
                
                # Ajouter un délai pour afficher la fin
                await asyncio.sleep(1)
                
                state_manager.is_searching = False
                
                # Nettoyer
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
                
                return result
            except Exception as e:
                # Nettoyer en cas d'erreur
                state_manager.is_searching = False
                if self.update_task:
                    self.update_task.cancel()
                    try:
                        await self.update_task
                    except asyncio.CancelledError:
                        pass
                
                error_msg = f"Erreur pendant la recherche: {e}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                console.print(f"[{THEME['error_color']}]{error_msg}[/{THEME['error_color']}]")
                
                return {"learnings": [], "visited_urls": {}}
    
    async def process_final_report(self, combined_query: str) -> Dict[str, Any]:
        """Traiter et afficher le rapport final"""
        result = {}
        learnings = state_manager.learnings
        visited_urls = state_manager.visited_urls
        tree_data = state_manager.tree_data
        start_time = state_manager.start_time
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
                
                report = self.ds.generate_final_report(combined_query, learnings, visited_urls)
                
                # Afficher un aperçu du rapport
                report_preview = report[:2000] + "... [suite du rapport]" if len(report) > 2000 else report
                md_report = Markdown(report_preview)
                console.print(Panel(
                    md_report,
                    title=f"[bold {THEME['success_color']}]{TRANSLATION['final_report']}[/bold {THEME['success_color']}]",
                    border_style=THEME['success_color'],
                    box=THEME['box_style']
                ))
                
                # Sauvegarder le rapport
                report_path = FileManager.save_markdown(report, combined_query.split("\n")[0])
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
                            FileManager.open_file(html_path)
                            # Utiliser Text au lieu de f-string pour éviter les problèmes de formatage
                            success_msg = Text(TRANSLATION["report_browser_opened"])
                            success_msg.stylize(f"bold {THEME['success_color']}")
                            console.print(success_msg)
                
                # Enregistrer le chemin du rapport
                state_manager.report_path = report_path
                result["report_path"] = report_path
                
                # Exporter un résumé de recherche complet
                summary_path = export_research_summary(
                    tree_data, 
                    visited_urls, 
                    combined_query.split("\n")[0], 
                    learnings, 
                    start_time, 
                    end_time
                )
                
                if summary_path:
                    logger.info(f"Résumé de recherche exporté: {summary_path}")
                
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
                            FileManager.open_file(graph_path)
                            # Utiliser Text au lieu de f-string pour éviter les problèmes de formatage
                            success_msg = Text(TRANSLATION["graph_browser_opened"])
                            success_msg.stylize(f"bold {THEME['success_color']}")
                            console.print(success_msg)
                        
                        # Enregistrer le chemin du graphique
                        state_manager.graph_path = graph_path
                        result["graph_path"] = graph_path
                
            except ResourceExhausted as e:
                error_msg = f"{TRANSLATION['error_quota']}\n{e}"
                logger.error(error_msg)
                console.print(Panel(
                    f"[{THEME['error_color']}]{error_msg}[/{THEME['error_color']}]",
                    border_style=THEME['error_color'],
                    box=THEME['box_style']
                ))
            except Exception as e:
                error_msg = f"{TRANSLATION['error_report']}: {e}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                console.print(Panel(
                    f"[{THEME['error_color']}]{error_msg}[/{THEME['error_color']}]",
                    border_style=THEME['error_color'],
                    box=THEME['box_style']
                ))
        else:
            console.print(Panel(
                f"[{THEME['info_color']}]{TRANSLATION['research_completed']}[/{THEME['info_color']}]",
                border_style=THEME['info_color'],
                box=THEME['box_style']
            ))
        
        # Retourner les informations de durée et les chemins
        result["duration"] = {
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": elapsed_time
        }
        
        return result
    
    async def run_research_interface(self) -> None:
        """Interface principale du laboratoire de recherche"""
        # Initialisation
        if not await self.initialize():
            return
        
        try:
            # Afficher l'écran de démarrage
            await self.show_splash_screen()
            
            # Afficher l'écran de bienvenue
            ComponentRegistry.get("welcome_screen")
            
            # Collecter les informations pour la recherche
            initial_query = Prompt.ask(f"[bold {THEME['query_color']}]{TRANSLATION['enter_query']}[/]")
            mode = Prompt.ask(
                f"[bold {THEME['info_color']}]{TRANSLATION['select_mode']}[/]",
                choices=["fast", "balanced", "comprehensive"],
                default="balanced"
            )
            breadth = int(Prompt.ask(
                f"[bold {THEME['info_color']}]{TRANSLATION['select_breadth']}[/]",
                default="5"
            ))
            depth = int(Prompt.ask(
                f"[bold {THEME['info_color']}]{TRANSLATION['select_depth']}[/]",
                default="3"
            ))
            
            # Initialiser DeepSearch avec gestion d'erreurs
            try:
                self.ds = DeepSearch(api_key=self.api_key, mode=mode)
            except Exception as e:
                error_msg = f"Erreur lors de l'initialisation de DeepSearch: {e}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                console.print(Panel(
                    f"[{THEME['error_color']}]{error_msg}[/{THEME['error_color']}]",
                    border_style=THEME['error_color'],
                    box=THEME['box_style']
                ))
                return
            
            # Générer et poser des questions de suivi
            follow_up_answers = await self.ask_follow_up_questions(initial_query)
            
            # Combiner la requête avec les questions de suivi
            combined_query = self.combine_query(initial_query, follow_up_answers)
            if follow_up_answers:
                console.print(Panel(
                    f"[{THEME['info_color']}]{TRANSLATION['combined_query']}\n{combined_query}[/{THEME['info_color']}]",
                    border_style=THEME['info_color'],
                    box=THEME['box_style']
                ))
            
            # Lancer la recherche
            result = await self.run_research(combined_query, breadth, depth)
            
            # Lire l'arbre final depuis le gestionnaire d'état
            tree_data = state_manager.tree_data
            
            # Afficher les résultats de la recherche
            console.clear()
            results_layout = Layout()
            results_layout.split_row(
                Layout(ComponentRegistry.get("tree", tree_data=tree_data), name="tree", ratio=3),
                Layout(ComponentRegistry.get("dashboard", 
                                         tree_data=tree_data, 
                                         visited_urls=state_manager.visited_urls, 
                                         start_time=state_manager.start_time), name="dashboard", ratio=2)
            )
            
            console.print(results_layout)
            
            # Notification pour les questions de suivi
            if mode == "comprehensive":
                ComponentRegistry.get("follow_up_notice", mode=mode)
            
            # Enregistrer l'arbre de recherche final
            if tree_data:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"research_tree_{timestamp}.json"
                FileManager.save_json(tree_data, filename, "trees")
            
            # Traiter et générer le rapport final
            await self.process_final_report(combined_query)
            
        except KeyboardInterrupt:
            logger.info("Recherche interrompue par l'utilisateur")
            console.print(f"[bold {THEME['error_color']}]Recherche interrompue par l'utilisateur.[/bold {THEME['error_color']}]")
        except Exception as e:
            error_msg = f"Erreur inattendue: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            console.print(f"[bold {THEME['error_color']}]{error_msg}[/bold {THEME['error_color']}]")
            console.print(traceback.format_exc())


# Fonction principale exportée
async def run_research_interface():
    """Point d'entrée principal de l'interface de recherche"""
    controller = DeepResearchController()
    await controller.run_research_interface()