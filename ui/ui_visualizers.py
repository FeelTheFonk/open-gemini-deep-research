"""
UI Visualizers - Visualisations avancées et exports de données
"""

import datetime
import uuid
import os
from pathlib import Path

from .ui_core import console, THEME, TRANSLATION, save_json, REPORTS_DIR, BASE_DIR


def export_html(markdown_path, query):
    """Exporte le rapport Markdown en HTML"""
    if not markdown_path or not os.path.exists(markdown_path):
        return None
    
    html_path = markdown_path.replace(".md", ".html")
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Création d'un HTML basique avec style
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de recherche: {query}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 1.5em;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        .date {{
            color: #7f8c8d;
            font-style: italic;
        }}
        /* Ajout de classes pour la mise en page avancée */
        .highlight {{
            background-color: #ffffcc;
            padding: 2px;
        }}
        .note {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .warning {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        @media print {{
            body {{
                max-width: none;
                padding: 0.5cm;
            }}
        }}
    </style>
</head>
<body>
    <div class="date">{datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
    <div id="content">
    <!-- Contenu Markdown converti -->
    
    </div>
    <script>
    // Charger la bibliothèque Markdown-it depuis un CDN
    document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.3.2/markdown-it.min.js"><\\/script>');
    window.onload = function() {{
        // Initialiser markdown-it
        const md = window.markdownit({{
            html: true,
            linkify: true,
            typographer: true
        }});
        
        // Convertir le Markdown en HTML
        const markdownContent = `{markdown_content.replace('`', '\\`')}`;
        const htmlContent = md.render(markdownContent);
        
        // Insérer dans la page
        document.getElementById('content').innerHTML = htmlContent;
    }};
    </script>
</body>
</html>"""
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return html_path
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de l'exportation HTML: {e}[/{THEME['error_color']}]")
        return None

def generate_knowledge_graph(tree_data, visited_urls):
    """Génère un graphique de connaissances au format HTML/JS utilisant d3.js"""
    if not tree_data:
        return None
    
    # Extraire les nœuds (requêtes) et les points de connaissance
    nodes = []
    links = []
    learnings = []
    
    def extract_nodes(node, parent_id=None):
        node_id = node.get("id", str(uuid.uuid4()))
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
        
        # Traiter récursivement les sous-requêtes
        for child in node.get("sub_queries", []):
            extract_nodes(child, node_id)
    
    # Démarrer l'extraction depuis la racine
    extract_nodes(tree_data)
    
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
        
        # Lier avec quelques connaissances pertinentes (simulation)
        # Dans une implémentation réelle, on aurait une correspondance exacte
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
            
            // Simulation de forces
            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(50));
            
            // Lignes pour les liens
            const link = g.append("g")
                .selectAll("line")
                .data(links)
                .enter()
                .append("line")
                .attr("class", "link")
                .attr("stroke-width", d => d.value);
            
            // Nœuds
            const node = g.append("g")
                .selectAll("circle")
                .data(nodes)
                .enter()
                .append("circle")
                .attr("class", d => `node node-${{d.type}} status-${{d.status || 'normal'}}`)
                .attr("r", d => d.type === "query" ? 15 : (d.type === "source" ? 12 : 8))
                .on("mouseover", function(event, d) {{
                    // Afficher info-bulle
                    tooltip.style("opacity", 1)
                        .html(`<strong>${{d.type === "query" ? "Requête" : (d.type === "source" ? "Source" : "Connaissance")}}</strong><br>${{d.full_text || d.label}}`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 20) + "px");
                }})
                .on("mouseout", function() {{
                    // Cacher info-bulle
                    tooltip.style("opacity", 0);
                }})
                .on("click", function(event, d) {{
                    if (d.type === "source" && d.url) {{
                        window.open(d.url, '_blank');
                    }}
                }})
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // Étiquettes de texte
            const text = g.append("g")
                .selectAll("text")
                .data(nodes)
                .enter()
                .append("text")
                .text(d => {{
                    const shortLabel = d.label.length > 20 ? d.label.substring(0, 20) + "..." : d.label;
                    return shortLabel;
                }})
                .attr("dy", 25)
                .attr("text-anchor", "middle")
                .attr("font-size", "10px");
            
            // Mise à jour de la position lors de la simulation
            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("cx", d => d.x = Math.max(20, Math.min(width - 20, d.x)))
                    .attr("cy", d => d.y = Math.max(20, Math.min(height - 20, d.y)));
                
                text
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
            }});
            
            // Fonctions drag
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
                d.fx = null;
                d.fy = null;
            }}
            
            // Contrôles
            document.getElementById("btnZoomIn").addEventListener("click", () => {{
                svg.transition().call(zoom.scaleBy, 1.5);
            }});
            
            document.getElementById("btnZoomOut").addEventListener("click", () => {{
                svg.transition().call(zoom.scaleBy, 0.75);
            }});
            
            document.getElementById("btnReset").addEventListener("click", () => {{
                svg.transition().call(zoom.transform, d3.zoomIdentity);
            }});
            
            document.getElementById("btnToggleQueries").addEventListener("click", () => {{
                const currentDisplay = node.filter(d => d.type === "query").style("display");
                node.filter(d => d.type === "query")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
                text.filter(d => d.type === "query")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
            }});
            
            document.getElementById("btnToggleLearnings").addEventListener("click", () => {{
                const currentDisplay = node.filter(d => d.type === "learning").style("display");
                node.filter(d => d.type === "learning")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
                text.filter(d => d.type === "learning")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
            }});
            
            document.getElementById("btnToggleSources").addEventListener("click", () => {{
                const currentDisplay = node.filter(d => d.type === "source").style("display");
                node.filter(d => d.type === "source")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
                text.filter(d => d.type === "source")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
            }});
        </script>
    </body>
    </html>
    """
    
    # Sauvegarder le fichier HTML
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    graph_path = REPORTS_DIR / f"knowledge_graph_{timestamp}.html"
    
    try:
        with open(graph_path, "w", encoding="utf-8") as f:
            f.write(html)
        return str(graph_path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de la création du graphique de connaissances: {e}[/{THEME['error_color']}]")
        return None

def export_research_summary(tree_data, visited_urls, query, learnings, start_time, end_time):
    """Exporte un résumé complet de la recherche au format JSON"""
    if not tree_data:
        return None
    
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Collecter les statistiques
    total_nodes, completed_nodes = 0, 0
    knowledge_count = 0
    
    def count_tree_stats(node):
        nonlocal total_nodes, completed_nodes, knowledge_count
        if node:
            total_nodes += 1
            if node.get("status") == "completed":
                completed_nodes += 1
            knowledge_count += len(node.get("learnings", []))
            for child in node.get("sub_queries", []):
                count_tree_stats(child)
    
    count_tree_stats(tree_data)
    
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
    safe_query = query.replace(" ", "_")[:30]
    filename = f"research_summary_{safe_query}_{timestamp}.json"
    summary_path = Path(BASE_DIR) / "summaries" / filename
    
    # Créer le dossier si nécessaire
    summary_path.parent.mkdir(exist_ok=True, parents=True)
    
    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            import json
            json.dump(summary, f, indent=2)
        return str(summary_path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de l'exportation du résumé: {e}[/{THEME['error_color']}]")
        return None