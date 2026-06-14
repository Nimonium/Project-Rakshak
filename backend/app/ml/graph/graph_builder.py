import networkx as nx
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)

class GraphBuilder:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_transaction(self, sender_id: str, receiver_id: str, amount: float, tx_id: str):
        """Adds a transaction edge between two accounts."""
        if self.G.has_edge(sender_id, receiver_id):
            self.G[sender_id][receiver_id]['weight'] += amount
            self.G[sender_id][receiver_id]['count'] += 1
            self.G[sender_id][receiver_id]['tx_ids'].append(tx_id)
        else:
            self.G.add_edge(sender_id, receiver_id, weight=amount, count=1, tx_ids=[tx_id], type='transaction')

    def add_shared_device(self, account_id1: str, account_id2: str, device_id: str):
        """Adds an undirected edge for a shared device."""
        self.G.add_edge(account_id1, account_id2, type='shared_device', device_id=device_id)
        self.G.add_edge(account_id2, account_id1, type='shared_device', device_id=device_id)

    def add_shared_ip(self, account_id1: str, account_id2: str, ip_address: str):
        """Adds an undirected edge for a shared IP."""
        self.G.add_edge(account_id1, account_id2, type='shared_ip', ip=ip_address)
        self.G.add_edge(account_id2, account_id1, type='shared_ip', ip=ip_address)

    def get_graph(self) -> nx.DiGraph:
        return self.G

    def clear(self):
        self.G.clear()
