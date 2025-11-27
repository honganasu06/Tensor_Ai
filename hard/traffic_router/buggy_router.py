"""
BUGGY VERSION OF TRAFFIC ROUTER - Intentionally contains bugs for debugging exercise
This version has 5 intentional bugs (and 2 decoys that appear to be bugs but aren't)
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


class BuggyTrafficRouter:
    """
    BUGGY VERSION - Contains intentional bugs for debugging exercise
    """
    
    def __init__(self, graph: Graph, fuel_consumption_rate: float = 1.0):
        """Initialize the router"""
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
        BUGGY VERSION with intentional issues
        """
        
        pq = []
        visited = set()
        best_state: Dict = {}
        
        initial_fuel = self.graph.max_fuel_capacity
        heapq.heappush(pq, (0, start, [start], 0.0, 0.0, initial_fuel, []))
        best_state[start] = (0, [start], 0.0, 0.0, initial_fuel, [])
        
        while pq:
            cost, current_node, route, distance, toll, current_fuel, fuel_stops = heapq.heappop(pq)
            
            if debug:
                print(f"Visiting {current_node}: cost=${cost:.2f}, distance={distance:.2f}km, fuel={current_fuel:.2f}")
            
            # BUG #1: visited check placed AFTER popping, causing infinite loops
            # (This is the most critical bug - allows revisiting nodes)
            
            neighbors = self.graph.get_neighbors(current_node)
            
            for neighbor_name, edge in neighbors:
                # BUG #2: visited check is too late - should happen before processing
                if neighbor_name in visited:
                    continue
                
                # BUG #3: Wrong order - checking toll BEFORE fuel constraints
                # This can cause paths to be rejected due to toll even when fuel is the real issue
                if toll + edge.toll_cost > max_toll:
                    if debug:
                        print(f"  -> {neighbor_name}: SKIP (toll)")
                    continue
                
                fuel_needed = edge.distance * self.fuel_consumption_rate
                
                # BUG #4: Off-by-one fuel calculation
                # Using fuel_needed * 0.9 instead of actual fuel_needed (underestimation)
                if current_fuel < (fuel_needed * 0.9):  # WRONG!
                    if self.graph.has_fuel_station(current_node):
                        new_fuel = self.graph.max_fuel_capacity
                        new_fuel_stops = fuel_stops + [current_node]
                        
                        if new_fuel < fuel_needed:
                            if debug:
                                print(f"  -> {neighbor_name}: SKIP (range)")
                            continue
                    else:
                        if debug:
                            print(f"  -> {neighbor_name}: SKIP (fuel)")
                        continue
                else:
                    new_fuel = current_fuel
                    new_fuel_stops = fuel_stops
                
                # BUG #5: Cost combination in wrong order (traffic penalty applied before toll in calculation)
                # This is subtle and causes incorrect cost comparisons
                edge_cost = edge.toll_cost + edge.distance + (edge.distance * edge.traffic_penalty)  # Wrong order!
                new_total_cost = cost + edge_cost
                new_distance = distance + edge.distance
                new_toll = toll + edge.toll_cost
                new_fuel = new_fuel - fuel_needed
                
                if neighbor_name not in best_state or new_total_cost <= best_state[neighbor_name][0]:  # DECOY: <= vs < (not actually a bug for this use case)
                    best_state[neighbor_name] = (new_total_cost, route + [neighbor_name], new_distance, new_toll, new_fuel, new_fuel_stops)
                    heapq.heappush(
                        pq,
                        (new_total_cost, neighbor_name, route + [neighbor_name], new_distance, new_toll, new_fuel, new_fuel_stops)
                    )
                    
                    if debug:
                        print(f"  -> {neighbor_name}: Added (cost=${new_total_cost:.2f})")
            
            # BUG LOCATION: This should happen at the START of the loop, not here
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                return RouteResult(
                    route=route,
                    total_cost=cost,
                    fuel_stops=fuel_stops,
                    distance_traveled=distance,
                    valid=True
                )
        
        return RouteResult(
            route=[],
            total_cost=float('inf'),
            fuel_stops=[],
            distance_traveled=0,
            valid=False,
            error_message=f"No valid route found from {start} to {end}"
        )
