"""
Network representation module for communication nodes and elements.
"""
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Types of network nodes."""
    ROUTER = "router"
    SWITCH = "switch"
    HUB = "hub"
    ENDPOINT = "endpoint"
    REPEATER = "repeater"


@dataclass
class NetworkNode:
    """Represents a node in the network."""
    id: str
    node_type: NodeType
    capacity: float = 100.0  # Bandwidth capacity
    reliability: float = 0.99  # Reliability factor (0-1)
    position: Tuple[float, float] = (0.0, 0.0)  # X, Y coordinates
    current_load: float = 0.0
    is_critical: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class NetworkLink:
    """Represents a link between two nodes."""
    source_id: str
    target_id: str
    bandwidth: float = 100.0
    latency: float = 1.0  # milliseconds
    reliability: float = 0.99
    distance: float = 1.0
    is_backup: bool = False


class Network:
    """Represents a communication network."""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.links: List[NetworkLink] = []
        self.adjacency: Dict[str, Set[str]] = {}  # Adjacency list
    
    def add_node(self, node: NetworkNode):
        """Add a node to the network."""
        self.nodes[node.id] = node
        if node.id not in self.adjacency:
            self.adjacency[node.id] = set()
    
    def add_link(self, link: NetworkLink):
        """Add a link to the network."""
        if link.source_id not in self.nodes or link.target_id not in self.nodes:
            raise ValueError("Both nodes must exist in the network")
        
        self.links.append(link)
        self.adjacency[link.source_id].add(link.target_id)
        # For undirected graph, add reverse connection
        if link.target_id not in self.adjacency:
            self.adjacency[link.target_id] = set()
        self.adjacency[link.target_id].add(link.source_id)
    
    def get_neighbors(self, node_id: str) -> Set[str]:
        """Get all neighbors of a node."""
        return self.adjacency.get(node_id, set())
    
    def get_link(self, source_id: str, target_id: str) -> Optional[NetworkLink]:
        """Get link between two nodes."""
        for link in self.links:
            if (link.source_id == source_id and link.target_id == target_id) or \
               (link.source_id == target_id and link.target_id == source_id):
                return link
        return None
    
    def get_path_cost(self, path: List[str]) -> float:
        """Calculate total cost (latency) of a path."""
        if len(path) < 2:
            return 0.0
        
        total_cost = 0.0
        for i in range(len(path) - 1):
            link = self.get_link(path[i], path[i + 1])
            if link:
                total_cost += link.latency
        return total_cost
    
    def get_path_reliability(self, path: List[str]) -> float:
        """Calculate total reliability of a path."""
        if len(path) < 2:
            return 1.0
        
        reliability = 1.0
        for i in range(len(path) - 1):
            link = self.get_link(path[i], path[i + 1])
            node = self.nodes.get(path[i])
            if link:
                reliability *= link.reliability
            if node:
                reliability *= node.reliability
        return reliability

