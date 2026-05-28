import networkx as nx
import community.community_louvain as community_louvain # pip install python-louvain
import structlog
import os
import json
from typing import Dict, Any, List

logger = structlog.get_logger(__name__)

class GraphRiskEngine:
    def __init__(self, graph: nx.DiGraph, artifacts_dir: str = "artifacts/graph"):
        self.G = graph
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def calculate_centrality_scores(self) -> Dict[str, float]:
        """Calculates PageRank for all nodes to find highly central accounts."""
        try:
            return nx.pagerank(self.G, weight='weight')
        except Exception as e:
            logger.error(f"Error calculating PageRank: {str(e)}")
            return {}

    def calculate_betweenness(self) -> Dict[str, float]:
        """Calculates Betweenness Centrality for bottleneck detection."""
        try:
            return nx.betweenness_centrality(self.G, weight='weight')
        except Exception as e:
            logger.error(f"Error calculating Betweenness Centrality: {str(e)}")
            return {}

    def find_mule_chains(self, max_length: int = 5) -> List[List[str]]:
        """Finds paths indicative of layered transfers (A -> B -> C -> D)."""
        chains = []
        # Find all simple paths between nodes with no incoming edges and nodes with no outgoing edges
        sources = [n for n, d in self.G.in_degree() if d == 0]
        sinks = [n for n, d in self.G.out_degree() if d == 0]
        
        for source in sources:
            for sink in sinks:
                if nx.has_path(self.G, source, sink):
                    for path in nx.all_simple_paths(self.G, source, sink, cutoff=max_length):
                        if len(path) > 2: # At least one intermediary
                            chains.append(path)
        return chains
        
    def find_circular_movements(self) -> List[List[str]]:
        """Finds cycles in the graph indicative of circular fund movement."""
        try:
            cycles = list(nx.simple_cycles(self.G))
            # Export found cycles
            if cycles:
                self._export_json("circular_loops.json", {"loops": cycles})
            return [c for c in cycles if len(c) > 2]
        except Exception as e:
            logger.error(f"Error finding cycles: {str(e)}")
            return []

    def detect_communities(self) -> Dict[str, int]:
        """Uses Louvain community detection (on undirected version) to find dense clusters."""
        try:
            undirected_G = self.G.to_undirected()
            partition = community_louvain.best_partition(undirected_G, weight='weight')
            
            # Export partition
            self._export_json("community_partition.json", partition)
            return partition
        except Exception as e:
            logger.error(f"Error detecting communities: {str(e)}")
            return {}

    def _export_json(self, filename: str, data: Any):
        filepath = os.path.join(self.artifacts_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to export {filename}: {str(e)}")

    def compute_account_risk(self, account_id: str) -> float:
        """
        Computes a composite graph risk score for a specific account.
        Returns a score between 0.0 and 1.0.
        """
        if account_id not in self.G:
            return 0.0
            
        risk_score = 0.0
        
        # 1. High Fan-in or Fan-out
        in_degree = self.G.in_degree(account_id)
        out_degree = self.G.out_degree(account_id)
        
        if in_degree > 10 and out_degree < 2:
            risk_score += 0.3 # Potential collector account
        elif out_degree > 10 and in_degree < 2:
            risk_score += 0.3 # Potential distributor account
            
        # 2. Centrality Checks (requires pre-computation in a real system)
        # Here we do it on the fly for the local subgraph for simplicity
        local_subgraph = nx.ego_graph(self.G, account_id, radius=2)
        if len(local_subgraph) > 2:
            pr = nx.pagerank(local_subgraph)
            if pr.get(account_id, 0) > 0.3:
                risk_score += 0.2
                
        # 3. Check for cycles (Multi-hop scoring)
        try:
            cycles = list(nx.simple_cycles(local_subgraph))
            if any(account_id in cycle for cycle in cycles):
                risk_score += 0.5
                
            # Suspicious subgraph extraction
            if risk_score > 0.6:
                self._export_json(f"suspicious_subgraph_{account_id}.json", {
                    "nodes": list(local_subgraph.nodes()),
                    "risk": risk_score
                })
        except:
            pass
            
        return min(risk_score, 1.0)
