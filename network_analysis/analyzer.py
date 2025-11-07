"""
Network analyzer for failure points, routing, and device placement.
"""
from typing import Dict, List, Set, Tuple, Optional
from collections import deque
import heapq
from network_analysis.network import Network, NetworkNode, NetworkLink, NodeType
from network_analysis.rules import NetworkRules


class NetworkAnalyzer:
    """Analyzes networks for failure points, routing, and optimization."""
    
    def __init__(self, network: Network, rules: NetworkRules = None):
        self.network = network
        self.rules = rules or NetworkRules()
        if not self.rules.rules:
            # Load default rules
            self.rules.load_rules(self.rules.get_default_rules())
    
    def identify_failure_points(self) -> List[Dict]:
        """
        Identify potential failure points in the network.
        Returns list of failure point assessments.
        """
        failure_points = []
        
        for node_id, node in self.network.nodes.items():
            issues = []
            risk_score = 0.0
            
            # Check node load
            if "node_load" in self.rules.rules and self.rules.rules["node_load"].enabled:
                load = self.rules.evaluate_node_load(self.network, node_id)
                if load > self.rules.rules["node_load"].threshold:
                    issues.append(f"High load: {load:.2%}")
                    risk_score += load * self.rules.rules["node_load"].weight
            
            # Check reliability
            if "reliability" in self.rules.rules and self.rules.rules["reliability"].enabled:
                reliability = self.rules.evaluate_reliability(self.network, node_id)
                if reliability < self.rules.rules["reliability"].threshold:
                    issues.append(f"Low reliability: {reliability:.2%}")
                    risk_score += (1 - reliability) * self.rules.rules["reliability"].weight
            
            # Check criticality (single point of failure)
            if "criticality" in self.rules.rules and self.rules.rules["criticality"].enabled:
                neighbors = self.network.get_neighbors(node_id)
                if len(neighbors) == 1:
                    issues.append("Single connection - potential bottleneck")
                    risk_score += 0.5 * self.rules.rules["criticality"].weight
                elif len(neighbors) == 0:
                    issues.append("Isolated node")
                    risk_score += 1.0 * self.rules.rules["criticality"].weight
            
            # Check if node is a bridge (removal would disconnect network)
            if self._is_bridge_node(node_id):
                issues.append("Bridge node - removal would disconnect network")
                risk_score += 0.8 * self.rules.rules.get("criticality", 
                    self.rules.get_default_rules()["criticality"]).weight
            
            if issues or risk_score > 0.3:
                failure_points.append({
                    "node_id": node_id,
                    "node_type": node.node_type.value,
                    "risk_score": risk_score,
                    "issues": issues,
                    "position": node.position
                })
        
        # Check links
        for link in self.network.links:
            if link.reliability < 0.95:
                failure_points.append({
                    "link": f"{link.source_id} -> {link.target_id}",
                    "risk_score": 1 - link.reliability,
                    "issues": [f"Low link reliability: {link.reliability:.2%}"],
                    "latency": link.latency
                })
        
        return sorted(failure_points, key=lambda x: x["risk_score"], reverse=True)
    
    def _is_bridge_node(self, node_id: str) -> bool:
        """Check if removing a node would disconnect the network."""
        # Simplified check: if node has only one connection, it might be a bridge
        neighbors = self.network.get_neighbors(node_id)
        if len(neighbors) <= 1:
            return True
        
        # More complex: check if removing node disconnects any pair of other nodes
        # For simplicity, we'll check if it's the only connection between two subgraphs
        return False  # Placeholder for more complex analysis
    
    def find_optimal_route(self, source: str, target: str, 
                          optimize_for: str = "latency") -> Tuple[List[str], Dict]:
        """
        Find optimal route between two nodes.
        optimize_for: "latency", "reliability", or "balanced"
        """
        if source not in self.network.nodes or target not in self.network.nodes:
            raise ValueError("Source and target must exist in network")
        
        if optimize_for == "latency":
            return self._dijkstra_latency(source, target)
        elif optimize_for == "reliability":
            return self._dijkstra_reliability(source, target)
        else:  # balanced
            return self._dijkstra_balanced(source, target)
    
    def _dijkstra_latency(self, source: str, target: str) -> Tuple[List[str], Dict]:
        """Dijkstra's algorithm optimized for latency."""
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[source] = 0.0
        previous = {}
        pq = [(0.0, source)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == target:
                break
            
            for neighbor in self.network.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                link = self.network.get_link(current, neighbor)
                if link:
                    new_dist = current_dist + link.latency
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        if path[0] != source:
            return [], {"error": "No path found"}
        
        total_latency = self.network.get_path_cost(path)
        reliability = self.network.get_path_reliability(path)
        
        return path, {
            "total_latency": total_latency,
            "reliability": reliability,
            "hop_count": len(path) - 1
        }
    
    def _dijkstra_reliability(self, source: str, target: str) -> Tuple[List[str], Dict]:
        """Dijkstra's algorithm optimized for reliability (maximize product)."""
        # Use negative log for reliability to convert to minimization problem
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[source] = 0.0
        previous = {}
        pq = [(0.0, source)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == target:
                break
            
            for neighbor in self.network.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                link = self.network.get_link(current, neighbor)
                node = self.network.nodes.get(current)
                if link and node:
                    # Negative log of reliability (higher reliability = lower cost)
                    link_cost = -1 * (link.reliability * node.reliability)
                    new_dist = current_dist + link_cost
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        if path[0] != source:
            return [], {"error": "No path found"}
        
        total_latency = self.network.get_path_cost(path)
        reliability = self.network.get_path_reliability(path)
        
        return path, {
            "total_latency": total_latency,
            "reliability": reliability,
            "hop_count": len(path) - 1
        }
    
    def _dijkstra_balanced(self, source: str, target: str) -> Tuple[List[str], Dict]:
        """Balanced optimization considering both latency and reliability."""
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[source] = 0.0
        previous = {}
        pq = [(0.0, source)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == target:
                break
            
            for neighbor in self.network.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                link = self.network.get_link(current, neighbor)
                node = self.network.nodes.get(current)
                if link and node:
                    # Combined metric: latency * (1 - reliability)
                    cost = link.latency * (2 - link.reliability - node.reliability)
                    new_dist = current_dist + cost
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        
        if path[0] != source:
            return [], {"error": "No path found"}
        
        total_latency = self.network.get_path_cost(path)
        reliability = self.network.get_path_reliability(path)
        
        return path, {
            "total_latency": total_latency,
            "reliability": reliability,
            "hop_count": len(path) - 1
        }
    
    def suggest_device_placements(self, device_type: NodeType = NodeType.REPEATER,
                                 max_devices: int = 5) -> List[Dict]:
        """
        Suggest optimal placements for devices (repeaters, etc.).
        """
        suggestions = []
        
        # Find long paths that could benefit from repeaters
        failure_points = self.identify_failure_points()
        
        # Identify areas with high latency or low reliability
        for failure_point in failure_points[:max_devices]:
            if "node_id" in failure_point:
                node = self.network.nodes.get(failure_point["node_id"])
                if node:
                    suggestions.append({
                        "device_type": device_type.value,
                        "position": node.position,
                        "near_node": failure_point["node_id"],
                        "reason": "; ".join(failure_point["issues"]),
                        "priority": failure_point["risk_score"]
                    })
        
        # Find links with high latency
        high_latency_links = sorted(
            [link for link in self.network.links if link.latency > 20.0],
            key=lambda x: x.latency,
            reverse=True
        )[:max_devices]
        
        for link in high_latency_links:
            source_node = self.network.nodes.get(link.source_id)
            target_node = self.network.nodes.get(link.target_id)
            if source_node and target_node:
                # Suggest placement at midpoint
                mid_x = (source_node.position[0] + target_node.position[0]) / 2
                mid_y = (source_node.position[1] + target_node.position[1]) / 2
                suggestions.append({
                    "device_type": device_type.value,
                    "position": (mid_x, mid_y),
                    "near_link": f"{link.source_id} -> {link.target_id}",
                    "reason": f"High latency link: {link.latency}ms",
                    "priority": link.latency / 100.0
                })
        
        return sorted(suggestions, key=lambda x: x["priority"], reverse=True)
    
    def analyze_network_health(self) -> Dict:
        """Comprehensive network health analysis."""
        failure_points = self.identify_failure_points()
        
        total_nodes = len(self.network.nodes)
        total_links = len(self.network.links)
        
        high_risk_nodes = len([fp for fp in failure_points if "node_id" in fp and fp["risk_score"] > 0.5])
        
        avg_reliability = sum(
            node.reliability for node in self.network.nodes.values()
        ) / total_nodes if total_nodes > 0 else 0.0
        
        avg_latency = sum(
            link.latency for link in self.network.links
        ) / total_links if total_links > 0 else 0.0
        
        return {
            "total_nodes": total_nodes,
            "total_links": total_links,
            "high_risk_nodes": high_risk_nodes,
            "failure_points_count": len(failure_points),
            "average_reliability": avg_reliability,
            "average_latency": avg_latency,
            "health_score": max(0.0, 1.0 - (high_risk_nodes / total_nodes) if total_nodes > 0 else 0.0),
            "recommendations": self._generate_recommendations(failure_points)
        }
    
    def _generate_recommendations(self, failure_points: List[Dict]) -> List[str]:
        """Generate recommendations based on failure points."""
        recommendations = []
        
        high_risk = [fp for fp in failure_points if fp.get("risk_score", 0) > 0.7]
        if high_risk:
            recommendations.append(f"Immediate attention required for {len(high_risk)} high-risk components")
        
        low_reliability = [fp for fp in failure_points if any("reliability" in issue.lower() for issue in fp.get("issues", []))]
        if low_reliability:
            recommendations.append("Consider replacing or upgrading low-reliability components")
        
        single_connections = [fp for fp in failure_points if "Single connection" in str(fp.get("issues", []))]
        if single_connections:
            recommendations.append("Add redundant connections for single-connection nodes")
        
        return recommendations

