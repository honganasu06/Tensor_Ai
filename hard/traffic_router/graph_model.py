"""
Graph Model for Traffic Router
Defines the structure of nodes (cities/intersections) and edges (roads)
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class Edge:
    """Represents a road between two nodes"""
    to_node: str
    distance: float  # Base distance in km
    traffic_penalty: float  # Additional time penalty (0-1, representing congestion index)
    toll_cost: float  # Toll in currency units
    
    def calculate_cost(self) -> float:
        """
        Calculate total cost of traversing this edge
        Cost = distance + (distance * traffic_penalty) + toll_cost
        """
        return self.distance + (self.distance * self.traffic_penalty) + self.toll_cost


@dataclass
class Node:
    """Represents a city or intersection"""
    name: str
    has_fuel_station: bool = False
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.name == other.name
        return self.name == other


class Graph:
    """
    Represents a weighted, bidirectional road network
    """
    
    def __init__(self, max_fuel_capacity: float):
        """
        Initialize the graph
        
        Args:
            max_fuel_capacity: Maximum fuel tank capacity in units (e.g., liters)
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}
        self.max_fuel_capacity = max_fuel_capacity
    
    def add_node(self, name: str, has_fuel_station: bool = False) -> None:
        """Add a node (city/intersection) to the graph"""
        if name not in self.nodes:
            self.nodes[name] = Node(name, has_fuel_station)
    
    def add_edge(
        self,
        from_node: str,
        to_node: str,
        distance: float,
        traffic_penalty: float = 0.0,
        toll_cost: float = 0.0,
        bidirectional: bool = True
    ) -> None:
        """
        Add an edge (road) between two nodes
        
        Args:
            from_node: Starting node name
            to_node: Ending node name
            distance: Distance in km
            traffic_penalty: Congestion index (0-1)
            toll_cost: Toll cost in currency units
            bidirectional: If True, add edge in both directions
        """
        # Ensure nodes exist
        self.add_node(from_node)
        self.add_node(to_node)
        
        # Add forward edge
        if from_node not in self.edges:
            self.edges[from_node] = []
        
        edge = Edge(to_node, distance, traffic_penalty, toll_cost)
        self.edges[from_node].append(edge)
        
        # Add reverse edge if bidirectional
        if bidirectional:
            if to_node not in self.edges:
                self.edges[to_node] = []
            reverse_edge = Edge(from_node, distance, traffic_penalty, toll_cost)
            self.edges[to_node].append(reverse_edge)
    
    def get_neighbors(self, node: str) -> List[Tuple[str, Edge]]:
        """Get all neighbors of a node with their edge information"""
        if node not in self.edges:
            return []
        return [(edge.to_node, edge) for edge in self.edges[node]]
    
    def has_fuel_station(self, node: str) -> bool:
        """Check if a node has a fuel station"""
        if node not in self.nodes:
            return False
        return self.nodes[node].has_fuel_station
    
    def print_structure(self) -> None:
        """Print the graph structure for debugging"""
        print("\n=== Graph Structure ===")
        print(f"Max Fuel Capacity: {self.max_fuel_capacity}")
        print("\nNodes:")
        for name, node in self.nodes.items():
            fuel_info = " (FUEL STATION)" if node.has_fuel_station else ""
            print(f"  {name}{fuel_info}")
        
        print("\nEdges:")
        for from_node, edges in self.edges.items():
            for edge in edges:
                print(f"  {from_node} -> {edge.to_node}")
                print(f"    Distance: {edge.distance} km")
                print(f"    Traffic Penalty: {edge.traffic_penalty}")
                print(f"    Toll Cost: ${edge.toll_cost}")
                print(f"    Total Cost: ${edge.calculate_cost():.2f}")
