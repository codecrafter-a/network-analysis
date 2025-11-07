"""
Customizable rulesets for network evaluation.
"""
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field
from network_analysis.network import Network, NetworkNode, NetworkLink


@dataclass
class RuleConfig:
    """Configuration for a network evaluation rule."""
    name: str
    enabled: bool = True
    weight: float = 1.0
    threshold: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)


class NetworkRules:
    """Customizable ruleset for network evaluation."""
    
    def __init__(self):
        self.rules: Dict[str, RuleConfig] = {}
        self.custom_rules: Dict[str, Callable] = {}
    
    def register_rule(self, name: str, rule_func: Callable, config: RuleConfig = None):
        """Register a custom rule function."""
        if config is None:
            config = RuleConfig(name=name)
        self.rules[name] = config
        self.custom_rules[name] = rule_func
    
    def evaluate_node_load(self, network: Network, node_id: str) -> float:
        """Evaluate node load factor (0-1, higher is worse)."""
        node = network.nodes.get(node_id)
        if not node:
            return 1.0
        return min(node.current_load / node.capacity, 1.0) if node.capacity > 0 else 1.0
    
    def evaluate_link_utilization(self, network: Network, link: NetworkLink) -> float:
        """Evaluate link utilization factor."""
        # Simplified - in real scenario, track actual usage
        return 0.5  # Placeholder
    
    def evaluate_reliability(self, network: Network, node_id: str) -> float:
        """Evaluate node reliability (0-1, higher is better)."""
        node = network.nodes.get(node_id)
        if not node:
            return 0.0
        return node.reliability
    
    def evaluate_criticality(self, network: Network, node_id: str) -> float:
        """Evaluate how critical a node is based on connectivity."""
        neighbors = network.get_neighbors(node_id)
        # More neighbors = more critical
        return min(len(neighbors) / 10.0, 1.0)
    
    def evaluate_path_redundancy(self, network: Network, source: str, target: str) -> int:
        """Count number of disjoint paths between two nodes."""
        # Simplified: count all paths (not necessarily disjoint)
        paths = self._find_all_paths(network, source, target, max_depth=10)
        return len(paths)
    
    def _find_all_paths(self, network: Network, source: str, target: str, 
                       max_depth: int = 10, visited: set = None) -> List[List[str]]:
        """Find all paths between source and target."""
        if visited is None:
            visited = set()
        
        if source == target:
            return [[source]]
        
        if max_depth <= 0 or source in visited:
            return []
        
        visited.add(source)
        paths = []
        
        for neighbor in network.get_neighbors(source):
            if neighbor not in visited:
                sub_paths = self._find_all_paths(network, neighbor, target, 
                                                max_depth - 1, visited.copy())
                for path in sub_paths:
                    paths.append([source] + path)
        
        return paths
    
    def get_default_rules(self) -> Dict[str, RuleConfig]:
        """Get default rule configurations."""
        return {
            "node_load": RuleConfig(
                name="node_load",
                enabled=True,
                weight=1.0,
                threshold=0.8,
                parameters={"max_load": 0.9}
            ),
            "reliability": RuleConfig(
                name="reliability",
                enabled=True,
                weight=1.5,
                threshold=0.95,
                parameters={"min_reliability": 0.95}
            ),
            "criticality": RuleConfig(
                name="criticality",
                enabled=True,
                weight=1.2,
                threshold=0.5,
                parameters={}
            ),
            "path_redundancy": RuleConfig(
                name="path_redundancy",
                enabled=True,
                weight=1.0,
                threshold=2,
                parameters={"min_paths": 2}
            ),
            "link_latency": RuleConfig(
                name="link_latency",
                enabled=True,
                weight=0.8,
                threshold=50.0,
                parameters={"max_latency_ms": 50.0}
            )
        }
    
    def load_rules(self, configs: Dict[str, RuleConfig]):
        """Load rule configurations."""
        self.rules.update(configs)
    
    def update_rule(self, name: str, **kwargs):
        """Update a rule's configuration."""
        if name in self.rules:
            for key, value in kwargs.items():
                if hasattr(self.rules[name], key):
                    setattr(self.rules[name], key, value)

