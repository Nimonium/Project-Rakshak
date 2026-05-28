from fastapi import APIRouter
from typing import Dict, Any
import networkx as nx
from backend.app.services.scoring_service import global_graph_builder

router = APIRouter()

@router.get("/{account_id}")
async def get_graph(account_id: str, depth: int = 2, prune_threshold: float = 0.0):
    """
    Returns the graph nodes and edges for the given account's local neighborhood.
    Allows configurable depth and edge pruning for cleaner visualization.
    """
    G = global_graph_builder.get_graph()
    if account_id not in G:
        return {"nodes": [], "edges": [], "suspicious_paths": []}
        
    subgraph = nx.ego_graph(G, account_id, radius=depth)
    
    # Prune edges below threshold (e.g. low amount transfers)
    if prune_threshold > 0:
        edges_to_remove = [(u, v) for u, v, d in subgraph.edges(data=True) if d.get('weight', 0) < prune_threshold]
        subgraph.remove_edges_from(edges_to_remove)
        # Remove isolated nodes after pruning
        subgraph.remove_nodes_from(list(nx.isolates(subgraph)))
    
    nodes = [{"id": n, "data": G.nodes[n]} for n in subgraph.nodes()]
    edges = [{"source": u, "target": v, "data": d} for u, v, d in subgraph.edges(data=True)]
    
    # Extract suspicious paths (mule chains) within this subgraph
    suspicious_paths = []
    sources = [n for n, d in subgraph.in_degree() if d == 0]
    sinks = [n for n, d in subgraph.out_degree() if d == 0]
    
    for source in sources:
        for sink in sinks:
            if nx.has_path(subgraph, source, sink):
                for path in nx.all_simple_paths(subgraph, source, sink, cutoff=4):
                    if len(path) > 2: # Potential chain
                        suspicious_paths.append(path)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "suspicious_paths": suspicious_paths
    }
