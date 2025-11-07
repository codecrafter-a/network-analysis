"""
Main entry point for network analysis application.
"""
import sys
import os

# Add parent directory to path to allow imports when running from this directory
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from network_analysis.network import Network, NetworkNode, NetworkLink, NodeType
from network_analysis.analyzer import NetworkAnalyzer
from network_analysis.rules import NetworkRules


def create_sample_network() -> Network:
    """Create a sample network for demonstration."""
    network = Network()
    
    # Create nodes
    nodes = [
        NetworkNode("A", NodeType.ROUTER, capacity=1000, reliability=0.99, position=(0, 0)),
        NetworkNode("B", NodeType.SWITCH, capacity=500, reliability=0.98, position=(10, 0)),
        NetworkNode("C", NodeType.SWITCH, capacity=500, reliability=0.97, position=(20, 0)),
        NetworkNode("D", NodeType.ENDPOINT, capacity=100, reliability=0.99, position=(10, 10)),
        NetworkNode("E", NodeType.ENDPOINT, capacity=100, reliability=0.99, position=(20, 10)),
        NetworkNode("F", NodeType.ROUTER, capacity=800, reliability=0.95, position=(30, 0)),
    ]
    
    for node in nodes:
        network.add_node(node)
    
    # Create links
    links = [
        NetworkLink("A", "B", bandwidth=1000, latency=5.0, reliability=0.99),
        NetworkLink("B", "C", bandwidth=500, latency=10.0, reliability=0.98),
        NetworkLink("B", "D", bandwidth=100, latency=2.0, reliability=0.99),
        NetworkLink("C", "E", bandwidth=100, latency=2.0, reliability=0.99),
        NetworkLink("C", "F", bandwidth=500, latency=15.0, reliability=0.90),  # Low reliability
        NetworkLink("F", "E", bandwidth=200, latency=8.0, reliability=0.95),
    ]
    
    for link in links:
        network.add_link(link)
    
    return network


def main():
    """Main function to demonstrate network analysis."""
    print("=" * 60)
    print("Network Analysis Application")
    print("=" * 60)
    
    # Create network
    network = create_sample_network()
    
    # Create rules
    rules = NetworkRules()
    rules.load_rules(rules.get_default_rules())
    
    # Create analyzer
    analyzer = NetworkAnalyzer(network, rules)
    
    # Analyze network health
    print("\n1. Network Health Analysis")
    print("-" * 60)
    health = analyzer.analyze_network_health()
    for key, value in health.items():
        if key != "recommendations":
            print(f"  {key}: {value}")
    print("\n  Recommendations:")
    for rec in health["recommendations"]:
        print(f"    - {rec}")
    
    # Identify failure points
    print("\n2. Failure Point Analysis")
    print("-" * 60)
    failure_points = analyzer.identify_failure_points()
    for i, fp in enumerate(failure_points[:5], 1):
        print(f"\n  Failure Point {i}:")
        if "node_id" in fp:
            print(f"    Node: {fp['node_id']} ({fp['node_type']})")
        elif "link" in fp:
            print(f"    Link: {fp['link']}")
        print(f"    Risk Score: {fp['risk_score']:.2f}")
        print(f"    Issues: {', '.join(fp['issues'])}")
    
    # Find optimal routes
    print("\n3. Optimal Routing")
    print("-" * 60)
    routes = [
        ("A", "F", "latency"),
        ("A", "F", "reliability"),
        ("A", "F", "balanced"),
    ]
    
    for source, target, opt_type in routes:
        path, metrics = analyzer.find_optimal_route(source, target, optimize_for=opt_type)
        if path:
            print(f"\n  Route {source} -> {target} (optimize: {opt_type}):")
            print(f"    Path: {' -> '.join(path)}")
            print(f"    Latency: {metrics['total_latency']:.2f}ms")
            print(f"    Reliability: {metrics['reliability']:.2%}")
            print(f"    Hops: {metrics['hop_count']}")
    
    # Suggest device placements
    print("\n4. Device Placement Suggestions")
    print("-" * 60)
    suggestions = analyzer.suggest_device_placements(max_devices=3)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n  Suggestion {i}:")
        print(f"    Device: {suggestion['device_type']}")
        print(f"    Position: {suggestion['position']}")
        print(f"    Reason: {suggestion['reason']}")
        print(f"    Priority: {suggestion['priority']:.2f}")
    
    # Demonstrate custom rules
    print("\n5. Custom Rules Example")
    print("-" * 60)
    rules.update_rule("node_load", threshold=0.7, weight=1.5)
    print("  Updated node_load rule: threshold=0.7, weight=1.5")
    print("  Re-analyzing with updated rules...")
    
    failure_points_updated = analyzer.identify_failure_points()
    print(f"  Failure points found: {len(failure_points_updated)}")


if __name__ == "__main__":
    main()

