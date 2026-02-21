from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Dict, Any
from semrag.graph_store.interface import IGraphStore

router = APIRouter()

# Dependency injection for the IGraphStore (must be provided at app setup)
graph_store: IGraphStore = None

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """
    Renders the Cytoscape.js based graph dashboard.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SEMRAG v3 Knowledge Dashboard</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
        <style>
            #cy { width: 100%; height: 600px; background-color: #111; display: block; border: 1px solid #444; }
            body { background-color: #000; color: #fff; font-family: sans-serif; }
            .sidebar { position: absolute; top: 10px; left: 10px; z-index: 100; background: rgba(0,0,0,0.7); padding: 10px; border: 1px solid #555; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3>SEMRAG v3 Graph</h3>
            <div id="details">Click a node for metadata</div>
        </div>
        <div id="cy"></div>
        <script>
            fetch('/dashboard/data')
                .then(res => res.json())
                .then(data => {
                    var cy = cytoscape({
                        container: document.getElementById('cy'),
                        elements: data.elements,
                        style: [
                            { selector: 'node', style: { 'label': 'data(label)', 'background-color': '#0074D9', 'color': '#fff' } },
                            { selector: 'edge', style: { 'label': 'data(label)', 'line-color': '#777', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#777', 'color': '#ccc' } }
                        ],
                        layout: { name: 'cose', animate: true }
                    });
                    
                    cy.on('tap', 'node', function(evt){
                        var node = evt.target;
                        document.getElementById('details').innerHTML = 
                            '<b>' + node.data('label') + '</b><br/>' +
                            'Provenance: ' + node.data('provenance') + '<br/>' +
                            'Namespace: ' + node.data('namespace') + '<br/>' +
                            'Confidence: ' + node.data('confidence');
                    });
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/dashboard/data")
async def get_dashboard_data():
    """
    Returns graph data in Cytoscape-compatible format.
    """
    # 1. Query for all entities and relationships
    # Note: For production, we would limit the nodes or use pagination.
    cypher = "MATCH (n)-[r]->(m) RETURN n.name as source_id, type(r) as rel, m.name as target_id, " 
             "n.provenance as s_prov, n.namespace as s_ns, n.confidence as s_conf, " 
             "m.provenance as t_prov, m.namespace as t_ns, m.confidence as t_conf, " 
             "r.provenance as r_prov, r.namespace as r_ns, r.confidence as r_conf LIMIT 500"
    
    results = graph_store.query(cypher)
    
    elements = []
    seen_nodes = set()
    
    for row in results:
        # Add source node
        if row['source_id'] not in seen_nodes:
            elements.append({
                "data": { "id": row['source_id'], "label": row['source_id'], 
                          "provenance": row['s_prov'], "namespace": row['s_ns'], "confidence": row['s_conf'] }
            })
            seen_nodes.add(row['source_id'])
            
        # Add target node
        if row['target_id'] not in seen_nodes:
            elements.append({
                "data": { "id": row['target_id'], "label": row['target_id'], 
                          "provenance": row['t_prov'], "namespace": row['t_ns'], "confidence": row['t_conf'] }
            })
            seen_nodes.add(row['target_id'])
            
        # Add relationship edge
        elements.append({
            "data": { "id": f"{row['source_id']}_{row['rel']}_{row['target_id']}", 
                      "source": row['source_id'], "target": row['target_id'], "label": row['rel'],
                      "provenance": row['r_prov'], "namespace": row['r_ns'], "confidence": row['r_conf'] }
        })
        
    return JSONResponse(content={"elements": elements})
