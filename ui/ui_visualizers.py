"""
UI Visualizers - Visualisations avancées et exports de données
Implémente des fonctionnalités de conversion et visualisation de données
"""

import datetime
import uuid
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .ui_core import (
    console, THEME, TRANSLATION, PathManager,
    FileManager, logger, sanitize_filename, state_manager
)


class HTMLExporter:
    """Classe pour l'exportation de contenu en HTML avec templates"""
    
    @staticmethod
    def get_base_template() -> str:
        """Retourne le template HTML de base"""
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1.5em;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        code {
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 3px;
        }
        pre {
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .date {
            color: #7f8c8d;
            font-style: italic;
        }
        /* Classes avancées */
        .highlight {
            background-color: #ffffcc;
            padding: 2px;
        }
        .note {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .warning {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        @media print {
            body {
                max-width: none;
                padding: 0.5cm;
            }
        }
    </style>
</head>
<body>
    <div class="date">{date}</div>
    <div id="content">
    {content}
    </div>
</body>
</html>"""
        
    @classmethod
    def export_markdown(cls, markdown_path: Union[str, Path], query: str) -> Optional[str]:
        """Exporte le rapport Markdown en HTML"""
        path_obj = Path(markdown_path) if isinstance(markdown_path, str) else markdown_path
        
        if not path_obj.exists():
            logger.error(f"Fichier Markdown non trouvé: {path_obj}")
            return None
        
        html_path = str(path_obj).replace(".md", ".html")
        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            
            # Version simplifiée sans formattage complexe
            html = f"""<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rapport de recherche: {query}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3, h4, h5, h6 {{ color: #2c3e50; margin-top: 1.5em; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            code {{ background-color: #f8f8f8; padding: 2px 4px; border-radius: 3px; }}
            pre {{ background-color: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; margin-left: 0; color: #666; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            img {{ max-width: 100%; height: auto; }}
            .date {{ color: #7f8c8d; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="date">{datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
        <div id="markdown-content" style="display:none;">{markdown_content.replace("`", "\\`")}</div>
        <div id="content"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.3.2/markdown-it.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var md = window.markdownit({{
                    html: true,
                    linkify: true,
                    typographer: true
                }});
                
                var markdownContent = document.getElementById('markdown-content').textContent;
                var htmlContent = md.render(markdownContent);
                
                document.getElementById('content').innerHTML = htmlContent;
            }});
        </script>
    </body>
    </html>"""
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            logger.info(f"Rapport HTML exporté: {html_path}")
            return html_path
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation HTML: {e}")
            console.print(f"[{THEME['error_color']}]Erreur lors de l'exportation HTML: {e}[/{THEME['error_color']}]")
            return None


class KnowledgeGraphGenerator:
    """Classe pour générer des graphiques de connaissances interactifs"""
    
    @staticmethod
    def generate(tree_data: Dict[str, Any], visited_urls: Dict[str, Any]) -> Optional[str]:
        """Génère un graphique de connaissances au format HTML/JS utilisant d3.js"""
        if not tree_data:
            logger.warning("Tentative de génération d'un graphique sans données d'arbre")
            return None
        
        # Extraction optimisée des nœuds (requêtes) et points de connaissance
        nodes = []
        links = []
        learnings = []
        node_ids = {}  # Pour éviter les doublons
        
        # Approche itérative pour l'extraction des nœuds
        def extract_nodes():
            queue = [(tree_data, None)]  # (node, parent_id)
            
            while queue:
                node, parent_id = queue.pop(0)
                if not node:
                    continue
                    
                node_id = node.get("id", str(uuid.uuid4()))
                # Éviter les doublons
                if node_id in node_ids:
                    if parent_id:
                        links.append({
                            "source": parent_id,
                            "target": node_id,
                            "value": 2
                        })
                    continue
                    
                node_ids[node_id] = True
                node_type = "query"
                node_label = node.get("query", "Unknown")
                node_status = node.get("status", "waiting")
                
                # Ajouter le nœud principal
                nodes.append({
                    "id": node_id,
                    "label": node_label,
                    "type": node_type,
                    "status": node_status
                })
                
                # Ajouter le lien avec le parent si applicable
                if parent_id:
                    links.append({
                        "source": parent_id,
                        "target": node_id,
                        "value": 2
                    })
                
                # Ajouter les connaissances acquises
                for i, learning in enumerate(node.get("learnings", [])):
                    learning_id = f"learning_{node_id}_{i}"
                    # Tronquer la connaissance si trop longue
                    short_learning = learning[:100] + "..." if len(learning) > 100 else learning
                    
                    # Ajouter le nœud de connaissance
                    nodes.append({
                        "id": learning_id,
                        "label": short_learning,
                        "type": "learning",
                        "full_text": learning
                    })
                    
                    # Lier la connaissance à la requête
                    links.append({
                        "source": node_id,
                        "target": learning_id,
                        "value": 1
                    })
                    
                    learnings.append({
                        "id": learning_id,
                        "text": learning,
                        "query": node_label
                    })
                
                # Traiter les sous-requêtes
                for child in node.get("sub_queries", []):
                    queue.append((child, node_id))
        
        # Exécuter l'extraction
        extract_nodes()
        
        # Ajouter les sources comme nœuds
        for i, (url_id, url_data) in enumerate(visited_urls.items()):
            source_id = f"source_{i}"
            source_title = url_data.get('title', 'Unknown Source')
            source_link = url_data.get('link', '#')
            
            # Ajouter le nœud de source
            nodes.append({
                "id": source_id,
                "label": source_title,
                "type": "source",
                "url": source_link
            })
            
            # Lier avec des connaissances pertinentes
            if learnings and i < len(learnings):
                links.append({
                    "source": source_id,
                    "target": learnings[i]["id"],
                    "value": 1
                })
        
        # Générer le HTML pour le graphique de connaissances
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Graphique des Connaissances</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    overflow: hidden;
                    background-color: #f8f9fa;
                }}
                #graph {{
                    width: 100vw;
                    height: 100vh;
                }}
                .node {{
                    stroke: #fff;
                    stroke-width: 1.5px;
                }}
                .link {{
                    stroke: #999;
                    stroke-opacity: 0.6;
                }}
                .node-query {{
                    fill: #3498db;
                }}
                .node-learning {{
                    fill: #2ecc71;
                }}
                .node-source {{
                    fill: #e74c3c;
                }}
                .status-completed {{
                    stroke: #2ecc71;
                    stroke-width: 3px;
                }}
                .status-in_progress {{
                    stroke: #f39c12;
                    stroke-width: 3px;
                }}
                .status-waiting {{
                    stroke: #95a5a6;
                    stroke-width: 3px;
                }}
                .tooltip {{
                    position: absolute;
                    background-color: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    max-width: 300px;
                    z-index: 1000;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.3s;
                }}
                .controls {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                button {{
                    margin: 5px;
                    padding: 5px 10px;
                    background-color: #3498db;
                    border: none;
                    color: white;
                    border-radius: 3px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #2980b9;
                }}
                .legend {{
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 12px;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 5px;
                }}
                .legend-color {{
                    width: 15px;
                    height: 15px;
                    margin-right: 5px;
                    border-radius: 50%;
                }}
            </style>
        </head>
        <body>
            <div id="graph"></div>
            <div class="tooltip" id="tooltip"></div>
            <div class="controls">
                <button id="btnZoomIn">Zoom +</button>
                <button id="btnZoomOut">Zoom -</button>
                <button id="btnReset">Reset</button>
                <button id="btnToggleQueries">Requêtes</button>
                <button id="btnToggleLearnings">Connaissances</button>
                <button id="btnToggleSources">Sources</button>
            </div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #3498db;"></div>
                    <span>Requête</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #2ecc71;"></div>
                    <span>Connaissance</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #e74c3c;"></div>
                    <span>Source</span>
                </div>
            </div>

            <script>
                // Données du graphique
                const nodes = {nodes};
                const links = {links};
                
                // Configuration
                const width = window.innerWidth;
                const height = window.innerHeight;
                const tooltip = d3.select("#tooltip");
                
                // Créer le SVG
                const svg = d3.select("#graph")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);
                    
                // Groupe pour zoom/pan
                const g = svg.append("g");
                
                // Zoom behavior
                const zoom = d3.zoom()
                    .scaleExtent([0.1, 4])
                    .on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }});
                    
                svg.call(zoom);
                
                // Simulation de forces avec paramètres optimisés
                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(d => d.type === "query" ? 50 : 30))
                    .alpha(0.3)
                    .alphaDecay(0.02);
                
                // Défintions des marqueurs pour les flèches
                svg.append("defs").selectAll("marker")
                    .data(["arrow"])
                    .enter()
                    .append("marker")
                    .attr("id", d => d)
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 15)
                    .attr("refY", 0)
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("d", "M0,-5L10,0L0,5")
                    .attr("fill", "#999");
                
                // Lignes pour les liens
                const link = g.append("g")
                    .selectAll("line")
                    .data(links)
                    .enter()
                    .append("line")
                    .attr("class", "link")
                    .attr("stroke-width", d => d.value)
                    .attr("marker-end", "url(#arrow)");
                
                // Groupes pour les nœuds
                const nodeGroup = g.append("g")
                    .selectAll("g")
                    .data(nodes)
                    .enter()
                    .append("g")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                // Cercles des nœuds
                nodeGroup.append("circle")
                    .attr("class", d => `node node-${{d.type}} status-${{d.status || 'normal'}}`)
                    .attr("r", d => d.type === "query" ? 15 : (d.type === "source" ? 12 : 8))
                    .on("mouseover", function(event, d) {{
                        // Afficher info-bulle
                        tooltip.style("opacity", 1)
                            .html(`<strong>${{d.type === "query" ? "Requête" : (d.type === "source" ? "Source" : "Connaissance")}}</strong><br>${{d.full_text || d.label}}`)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 20) + "px");
                        
                        // Mettre en évidence les connexions
                        link.style("stroke", l => 
                            l.source.id === d.id || l.target.id === d.id 
                                ? "#ff0000" 
                                : "#999")
                            .style("stroke-opacity", l => 
                                l.source.id === d.id || l.target.id === d.id 
                                    ? 1 
                                    : 0.6)
                            .style("stroke-width", l => 
                                l.source.id === d.id || l.target.id === d.id 
                                    ? l.value + 1 
                                    : l.value);
                    }})
                    .on("mouseout", function() {{
                        // Cacher info-bulle
                        tooltip.style("opacity", 0);
                        
                        // Réinitialiser les liens
                        link.style("stroke", "#999")
                            .style("stroke-opacity", 0.6)
                            .style("stroke-width", d => d.value);
                    }})
                    .on("click", function(event, d) {{
                        if (d.type === "source" && d.url) {{
                            window.open(d.url, '_blank');
                        }}
                    }});
                
                // Étiquettes de texte
                nodeGroup.append("text")
                    .text(d => {{
                        const shortLabel = d.label.length > 20 ? d.label.substring(0, 20) + "..." : d.label;
                        return shortLabel;
                    }})
                    .attr("dy", 25)
                    .attr("text-anchor", "middle")
                    .attr("font-size", "10px");
                
                // Mise à jour de la position lors de la simulation
                simulation.on("tick", () => {{
                    // Mise à jour optimisée avec limites
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    nodeGroup.attr("transform", d => `translate(${{
                        d.x = Math.max(20, Math.min(width - 20, d.x))
                    }},${{
                        d.y = Math.max(20, Math.min(height - 20, d.y))
                    }})`);
                }});
                
                // Fonctions drag améliorées
                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}
                
                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}
                
                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    // Permettre aux nœuds de rester fixés si l'utilisateur maintient Shift
                    if (!event.sourceEvent.shiftKey) {{
                        d.fx = null;
                        d.fy = null;
                    }}
                }}
                
                // Contrôles interactifs
                document.getElementById("btnZoomIn").addEventListener("click", () => {{
                    svg.transition().duration(300).call(zoom.scaleBy, 1.5);
                }});
                
                document.getElementById("btnZoomOut").addEventListener("click", () => {{
                    svg.transition().duration(300).call(zoom.scaleBy, 0.75);
                }});
                
                document.getElementById("btnReset").addEventListener("click", () => {{
                    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
                }});
                
                // Fonctions de filtrage optimisées
                function toggleNodeVisibility(nodeType, button) {{
                    const isVisible = !button.classList.contains('active');
                    button.classList.toggle('active');
                    
                    nodeGroup.filter(d => d.type === nodeType)
                        .style("display", isVisible ? "none" : null);
                        
                    // Mettre à jour les liens
                    link.style("display", function(d) {{
                        const source = nodes.find(n => n.id === d.source.id || n.id === d.source);
                        const target = nodes.find(n => n.id === d.target.id || n.id === d.target);
                        
                        // Vérifier si l'un des noeuds est caché
                        if ((source && source.type === nodeType && !isVisible) ||
                            (target && target.type === nodeType && !isVisible)) {{
                            return null;
                        }}
                        
                        return "none";
                    }});
                }}
                
                document.getElementById("btnToggleQueries").addEventListener("click", function() {{
                    toggleNodeVisibility("query", this);
                }});
                
                document.getElementById("btnToggleLearnings").addEventListener("click", function() {{
                    toggleNodeVisibility("learning", this);
                }});
                
                document.getElementById("btnToggleSources").addEventListener("click", function() {{
                    toggleNodeVisibility("source", this);
                }});
                
                // Optimisation pour grandes quantités de données
                if (nodes.length > 200) {{
                    console.log("Grand graphique détecté, optimisation appliquée");
                    simulation.alphaDecay(0.04); // Stabiliser plus rapidement
                }}
                
                // Adaptation au redimensionnement de fenêtre
                window.addEventListener('resize', function() {{
                    const width = window.innerWidth;
                    const height = window.innerHeight;
                    svg.attr('width', width).attr('height', height);
                    simulation.force("center", d3.forceCenter(width / 2, height / 2)).restart();
                }});
            </script>
        </body>
        </html>
        """
        
        # Sauvegarder le fichier HTML
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        graph_path = PathManager.get_path("graphs", f"knowledge_graph_{timestamp}.html")
        
        try:
            with open(graph_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"Graphique de connaissances généré: {graph_path}")
            return str(graph_path)
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique de connaissances: {e}")
            console.print(f"[{THEME['error_color']}]Erreur lors de la création du graphique de connaissances: {e}[/{THEME['error_color']}]")
            return None


class ResearchSummaryExporter:
    """Classe pour exporter des résumés de recherche"""
    
    @staticmethod
    def export_summary(tree_data: Dict[str, Any], visited_urls: Dict[str, Any], 
                       query: str, learnings: List[str], start_time: float, 
                       end_time: float) -> Optional[str]:
        """Exporte un résumé complet de la recherche au format JSON"""
        if not tree_data:
            logger.warning("Tentative d'exportation d'un résumé sans données d'arbre")
            return None
        
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        # Collecter les statistiques
        total_nodes, completed_nodes = 0, 0
        knowledge_count = 0
        
        # Utiliser des méthodes non récursives
        queue = [tree_data]
        while queue:
            node = queue.pop(0)
            if node:
                total_nodes += 1
                if node.get("status") == "completed":
                    completed_nodes += 1
                knowledge_count += len(node.get("learnings", []))
                queue.extend(node.get("sub_queries", []))
        
        # Créer le résumé de recherche
        summary = {
            "meta": {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "duration": {
                    "minutes": minutes,
                    "seconds": seconds,
                    "total_seconds": elapsed_time
                }
            },
            "statistics": {
                "total_queries": total_nodes,
                "completed_queries": completed_nodes,
                "completion_rate": (completed_nodes / total_nodes) if total_nodes > 0 else 0,
                "total_learnings": knowledge_count,
                "total_sources": len(visited_urls) if visited_urls else 0
            },
            "research_tree": tree_data,
            "learnings": learnings,
            "sources": visited_urls
        }
        
        # Sauvegarder le résumé
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = sanitize_filename(query, max_length=30)
        filename = f"research_summary_{safe_query}_{timestamp}.json"
        
        # Utiliser le FileManager pour la sauvegarde
        return FileManager.save_json(summary, filename, "summaries")


# Fonctions exportées pour compatibilité
export_html = HTMLExporter.export_markdown
generate_knowledge_graph = KnowledgeGraphGenerator.generate
export_research_summary = ResearchSummaryExporter.export_summary