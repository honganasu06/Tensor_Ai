"""
Traffic Router Implementation using Modified Dijkstra's Algorithm
Handles routing with distance, traffic, toll, and fuel constraints
"""

import heapq
from typing import List, Tuple, Optional, Dict
from graph_model import Graph, Edge


class RouteResult:
    """Represents the result of a routing query"""
    
    def __init__(
        self,
        route: List[str],
        total_cost: float,
        fuel_stops: List[str],
        distance_traveled: float,
        valid: bool = True,
        error_message: str = ""
    ):
        self.route = route
        self.total_cost = total_cost
        self.fuel_stops = fuel_stops
        self.distance_traveled = distance_traveled
        self.valid = valid
        self.error_message = error_message
    
    def __repr__(self):
        if not self.valid:
            return f"Invalid Route: {self.error_message}"
        
        stops_str = " -> ".join(self.route)
        if self.fuel_stops:
            return (
                f"Route: {stops_str}\n"
                f"Total Cost: ${self.total_cost:.2f}\n"
                f"Distance: {self.distance_traveled:.2f} km\n"
                f"Fuel Stops: {', '.join(self.fuel_stops)}"
            )
        else:
            return (
                f"Route: {stops_str}\n"
                f"Total Cost: ${self.total_cost:.2f}\n"
                f"Distance: {self.distance_traveled:.2f} km\n"
                f"Fuel Stops: None"
            )


class TrafficRouter:
    """
    Implements Dijkstra's algorithm with traffic, toll, and fuel constraints
    """
    
    def __init__(self, graph: Graph, fuel_consumption_rate: float = 1.0):
        """
        Initialize the router
        
        Args:
            graph: The road network graph
            fuel_consumption_rate: Fuel units consumed per km (default 1.0)
        """
        self.graph = graph
        self.fuel_consumption_rate = fuel_consumption_rate
    
    def find_optimal_route(
        self,
        start: str,
        end: str,
        max_toll: float = float('inf'),
        debug: bool = False
    ) -> RouteResult:
        """
        Find optimal route from start to end using modified Dijkstra's algorithm
        
        The algorithm considers:
        1. Base distance cost
        2. Traffic penalties
        3. Toll costs
        4. Fuel constraints (cannot travel if fuel would run out)
        
        Args:
            start: Starting node name
            end: Ending node name
            max_toll: Maximum acceptable total toll cost
            debug: Enable debug output
        
        Returns:
            RouteResult object with route, cost, and fuel stops
        """
        
        # Priority queue: (cost, node, route, distance_traveled, total_toll, current_fuel, fuel_stops)
        pq = []
        visited = set()
        
        # State tracking: node -> (min_cost, route, distance, toll, fuel, fuel_stops)
        best_state: Dict = {}
        
        # Start with full tank
        initial_fuel = self.graph.max_fuel_capacity
        heapq.heappush(pq, (0, start, [start], 0.0, 0.0, initial_fuel, []))
        
        best_state[start] = (0, [start], 0.0, 0.0, initial_fuel, [])
        
        while pq:
            cost, current_node, route, distance, toll, current_fuel, fuel_stops = heapq.heappop(pq)
            
            if debug:
                print(f"Visiting {current_node}: cost=${cost:.2f}, distance={distance:.2f}km, fuel={current_fuel:.2f}")
            
            # Skip if already visited with better or equal state
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Success - reached destination
            if current_node == end:
                return RouteResult(
                    route=route,
                    total_cost=cost,
                    fuel_stops=fuel_stops,
                    distance_traveled=distance,
                    valid=True
                )
            
            # Explore neighbors
            neighbors = self.graph.get_neighbors(current_node)
            
            for neighbor_name, edge in neighbors:
                if neighbor_name in visited:
                    continue
                
                # Calculate fuel needed for this edge
                fuel_needed = edge.distance * self.fuel_consumption_rate
                
                # Check if we have enough fuel
                if current_fuel < fuel_needed:
                    # Can we refuel at current node?
                    if self.graph.has_fuel_station(current_node):
                        # Refuel to full capacity
                        new_fuel = self.graph.max_fuel_capacity
                        new_fuel_stops = fuel_stops + [current_node]
                        
                        # Check again after refueling
                        if new_fuel < fuel_needed:
                            if debug:
                                print(f"  -> {neighbor_name}: SKIP (fuel range too short)")
                            continue
                    else:
                        if debug:
                            print(f"  -> {neighbor_name}: SKIP (insufficient fuel, no station)")
                        continue
                else:
                    new_fuel = current_fuel
                    new_fuel_stops = fuel_stops
                
                # Calculate new costs
                edge_cost = edge.calculate_cost()
                new_total_cost = cost + edge_cost
                new_distance = distance + edge.distance
                new_toll = toll + edge.toll_cost
                new_fuel = new_fuel - fuel_needed
                
                # Check toll constraint
                if new_toll > max_toll:
                    if debug:
                        print(f"  -> {neighbor_name}: SKIP (toll limit exceeded)")
                    continue
                
                # Only add if this is a better path to neighbor
                if neighbor_name not in best_state or new_total_cost < best_state[neighbor_name][0]:
                    best_state[neighbor_name] = (new_total_cost, route + [neighbor_name], new_distance, new_toll, new_fuel, new_fuel_stops)
                    heapq.heappush(
                        pq,
                        (new_total_cost, neighbor_name, route + [neighbor_name], new_distance, new_toll, new_fuel, new_fuel_stops)
                    )
                    
                    if debug:
                        print(f"  -> {neighbor_name}: Added (cost=${new_total_cost:.2f}, fuel={new_fuel:.2f})")
        
        # No path found
        return RouteResult(
            route=[],
            total_cost=float('inf'),
            fuel_stops=[],
            distance_traveled=0,
            valid=False,
            error_message=f"No valid route found from {start} to {end}"
        )
