#!/usr/bin/env python3
"""
QUICK START GUIDE - Traffic Router
Get up and running in 5 minutes
"""

# ============================================================================
# 1. BASIC USAGE (2 minutes)
# ============================================================================

"""
Step 1: Import required modules
"""
from graph_model import Graph
from router_implementation import TrafficRouter


"""
Step 2: Create a graph
"""
graph = Graph(max_fuel_capacity=20)


"""
Step 3: Add nodes (cities/intersections)
"""
graph.add_node("CityA", has_fuel_station=True)   # Has fuel station
graph.add_node("CityB", has_fuel_station=False)  # No fuel station
graph.add_node("CityC", has_fuel_station=True)


"""
Step 4: Add edges (roads)
Format: from, to, distance, traffic_penalty, toll_cost
"""
graph.add_edge(
    "CityA", "CityB",
    distance=10,
    traffic_penalty=0.2,  # 20% congestion
    toll_cost=0
)

graph.add_edge(
    "CityB", "CityC",
    distance=15,
    traffic_penalty=0.1,  # 10% congestion
    toll_cost=5           # $5 toll
)

graph.add_edge(
    "CityA", "CityC",
    distance=35,
    traffic_penalty=0.0,  # No congestion
    toll_cost=0
)


"""
Step 5: Create router
"""
router = TrafficRouter(graph, fuel_consumption_rate=1.0)
# fuel_consumption_rate = how much fuel per km


"""
Step 6: Find optimal route
"""
result = router.find_optimal_route(
    start="CityA",
    end="CityC",
    max_toll=20  # Won't use routes costing >$20 in tolls
)


"""
Step 7: Use the result
"""
if result.valid:
    print(f"Route found: {' -> '.join(result.route)}")
    print(f"Total cost: ${result.total_cost:.2f}")
    print(f"Distance: {result.distance_traveled} km")
    print(f"Fuel stops: {', '.join(result.fuel_stops) or 'None'}")
else:
    print(f"Error: {result.error_message}")


# ============================================================================
# 2. EXAMPLE: REAL-WORLD ROUTE (3 minutes)
# ============================================================================

def example_road_trip():
    """
    Example: Finding best route for a road trip
    """
    print("\n" + "="*60)
    print("ROAD TRIP PLANNER - New York to Boston")
    print("="*60)
    
    # Create graph for Northeast corridor
    graph = Graph(max_fuel_capacity=50)  # 50 gallons
    
    # Add cities with fuel availability
    cities = [
        ("NYC", True),
        ("Connecticut", False),
        ("Providence", False),
        ("Boston", True),
        ("Philadelphia", True),
    ]
    
    for city, has_station in cities:
        graph.add_node(city, has_fuel_station=has_station)
    
    # Add roads (distance in miles, traffic as percentage, toll in dollars)
    routes = [
        # I-95 corridor (main highway)
        ("NYC", "Connecticut", 40, 0.3, 8),      # Heavy traffic, tolls
        ("Connecticut", "Providence", 115, 0.1, 5),
        ("Providence", "Boston", 50, 0.2, 3),
        
        # Alternative route
        ("NYC", "Philadelphia", 95, 0.4, 6),
        ("Philadelphia", "Providence", 290, 0.0, 10),
        
        # Direct route
        ("NYC", "Boston", 215, 0.2, 18),
    ]
    
    for from_city, to_city, distance, traffic, toll in routes:
        graph.add_edge(from_city, to_city, distance, traffic, toll)
    
    # Create router with fuel consumption of 0.1 gal/mile
    router = TrafficRouter(graph, fuel_consumption_rate=0.1)
    
    # Scenario 1: Find cheapest route
    print("\nScenario 1: Find cheapest route")
    result1 = router.find_optimal_route("NYC", "Boston")
    print(f"  Route: {' -> '.join(result1.route)}")
    print(f"  Cost: ${result1.total_cost:.2f}")
    print(f"  Distance: {result1.distance_traveled} miles")
    print(f"  Fuel stops: {', '.join(result1.fuel_stops) or 'None'}")
    
    # Scenario 2: Avoid tolls (max $10)
    print("\nScenario 2: Minimize tolls (max $10)")
    result2 = router.find_optimal_route("NYC", "Boston", max_toll=10)
    if result2.valid:
        print(f"  Route: {' -> '.join(result2.route)}")
        print(f"  Cost: ${result2.total_cost:.2f}")
    else:
        print(f"  {result2.error_message}")


# ============================================================================
# 3. EXAMPLE: UNDERSTAND THE COST MODEL
# ============================================================================

def understand_cost_calculation():
    """
    Learn how costs are calculated
    """
    print("\n" + "="*60)
    print("UNDERSTANDING COST CALCULATION")
    print("="*60)
    
    from graph_model import Edge
    
    # Create different road types
    print("\nDifferent road types and their costs:")
    
    roads = [
        ("Clear highway", 100, 0.0, 0),
        ("Busy city street", 50, 0.5, 0),
        ("Toll road", 100, 0.0, 15),
        ("Congested toll road", 75, 0.4, 10),
    ]
    
    for name, distance, traffic, toll in roads:
        edge = Edge(to_node="destination", 
                   distance=distance, 
                   traffic_penalty=traffic,
                   toll_cost=toll)
        cost = edge.calculate_cost()
        
        breakdown = {
            "Base distance": distance,
            "Traffic penalty": distance * traffic,
            "Toll": toll,
            "Total cost": cost,
        }
        
        print(f"\n{name}:")
        print(f"  Distance: {distance} km")
        print(f"  Traffic: {int(traffic*100)}% congestion")
        print(f"  Toll: ${toll}")
        print(f"  → Total cost: ${cost:.2f}")
        
        print(f"     ({distance} + {distance*traffic:.1f} + {toll})")


# ============================================================================
# 4. EXAMPLE: DEBUGGING WITH DEBUG MODE
# ============================================================================

def debug_example():
    """
    Use debug mode to see algorithm in action
    """
    print("\n" + "="*60)
    print("DEBUGGING - STEP-BY-STEP EXECUTION")
    print("="*60)
    
    # Create simple graph
    graph = Graph(max_fuel_capacity=15)
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B")
    graph.add_node("C", has_fuel_station=True)
    
    graph.add_edge("A", "B", 5, 0.1, 0)
    graph.add_edge("B", "C", 8, 0.2, 1)
    
    router = TrafficRouter(graph, fuel_consumption_rate=1.0)
    
    print("\nFinding route A → C with DEBUG enabled:")
    print("(Shows each step of the algorithm)\n")
    
    result = router.find_optimal_route("A", "C", debug=True)
    
    print(f"\nFinal result:")
    print(result)


# ============================================================================
# 5. RUNNING TESTS
# ============================================================================

def run_tests():
    """
    Run the comprehensive test suite
    """
    print("\n" + "="*60)
    print("RUNNING TEST SUITE")
    print("="*60)
    
    from test_suite import (
        test_basic_path,
        test_fuel_constraint,
        test_toll_constraint,
        test_traffic_vs_distance,
        test_no_valid_path,
        test_multiple_paths_same_cost
    )
    
    tests = [
        ("Basic Path Finding", test_basic_path),
        ("Fuel Constraints", test_fuel_constraint),
        ("Toll Limits", test_toll_constraint),
        ("Traffic vs Distance", test_traffic_vs_distance),
        ("No Valid Path", test_no_valid_path),
        ("Multiple Equal Paths", test_multiple_paths_same_cost),
    ]
    
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        try:
            test_func()
        except Exception as e:
            print(f"Error: {e}")


# ============================================================================
# 6. UNDERSTANDING THE BUGS
# ============================================================================

def understand_bugs():
    """
    Learn about the intentional bugs
    """
    print("\n" + "="*60)
    print("UNDERSTANDING THE 5 BUGS")
    print("="*60)
    
    bugs = [
        {
            "number": 1,
            "name": "Visited Set Placement",
            "severity": "CRITICAL",
            "symptom": "Algorithm hangs or finds suboptimal routes",
            "cause": "Visited check at end of loop instead of start",
            "fix": "Move visited check to beginning of while loop",
        },
        {
            "number": 2,
            "name": "Off-by-One Fuel",
            "severity": "HIGH",
            "symptom": "Vehicle runs out of fuel mid-journey",
            "cause": "Using (fuel_needed * 0.9) instead of exact fuel_needed",
            "fix": "Remove the 0.9 multiplier, use exact value",
        },
        {
            "number": 3,
            "name": "Wrong Cost Order",
            "severity": "MEDIUM",
            "symptom": "Suboptimal routes chosen",
            "cause": "Toll added to edge cost instead of separately",
            "fix": "Separate toll from base routing cost calculation",
        },
        {
            "number": 4,
            "name": "Constraint Order",
            "severity": "MEDIUM",
            "symptom": "Confusing error messages",
            "cause": "Checking toll limit before fuel validation",
            "fix": "Check fuel first (hard constraint), toll second",
        },
        {
            "number": 5,
            "name": "Fuel Stops Tracking",
            "severity": "LOW",
            "symptom": "Incomplete fuel stops in result",
            "cause": "Inconsistent pattern in tracking refuels",
            "fix": "Always explicitly manage fuel_stops list",
        },
    ]
    
    for bug in bugs:
        print(f"\nBUG #{bug['number']}: {bug['name']}")
        print(f"  Severity: {bug['severity']}")
        print(f"  Symptom: {bug['symptom']}")
        print(f"  Cause: {bug['cause']}")
        print(f"  Fix: {bug['fix']}")


# ============================================================================
# 7. COMMON PATTERNS
# ============================================================================

def common_patterns():
    """
    Patterns for using Traffic Router
    """
    print("\n" + "="*60)
    print("COMMON USAGE PATTERNS")
    print("="*60)
    
    print("""
PATTERN 1: Find absolute cheapest route
────────────────────────────────────────
result = router.find_optimal_route(start, end)
# No constraints, algorithm finds mathematically optimal path


PATTERN 2: Budget-conscious routing
────────────────────────────────────────
result = router.find_optimal_route(start, end, max_toll=50)
# Won't use routes exceeding $50 in toll costs


PATTERN 3: Multiple queries on same graph
────────────────────────────────────────
# Create once, reuse many times (efficient)
router = TrafficRouter(graph)
result1 = router.find_optimal_route("A", "B")
result2 = router.find_optimal_route("A", "C")
result3 = router.find_optimal_route("B", "C")


PATTERN 4: Dynamic graph updates
────────────────────────────────────────
# Recreate graph when network changes
graph = Graph(max_fuel_capacity=20)
# ... add nodes and edges ...
router = TrafficRouter(graph)
result = router.find_optimal_route(start, end)

# Later, update with new information:
graph.add_edge(new_from, new_to, distance, traffic, toll)
router = TrafficRouter(graph)  # Recreate router
result = router.find_optimal_route(start, end)


PATTERN 5: Compare scenarios
────────────────────────────────────────
# Scenario 1: No budget limit
r1 = router.find_optimal_route("A", "B")

# Scenario 2: $20 budget
r2 = router.find_optimal_route("A", "B", max_toll=20)

# Scenario 3: $5 budget
r3 = router.find_optimal_route("A", "B", max_toll=5)

# Compare results
print(f"Unlimited: {r1.total_cost}")
print(f"$20 limit: {r2.total_cost if r2.valid else 'Invalid'}")
print(f"$5 limit: {r3.total_cost if r3.valid else 'Invalid'}")
    """)


# ============================================================================
# 8. MAIN - Choose what to run
# ============================================================================

def main():
    """
    Main entry point - demonstrates usage
    """
    print("\n" + "="*60)
    print("TRAFFIC ROUTER - QUICK START GUIDE")
    print("="*60)
    
    print("""
Choose what to learn:

1. Basic Usage (example_road_trip)
2. Cost Calculation (understand_cost_calculation)
3. Debug Mode (debug_example)
4. Test Suite (run_tests)
5. Bugs Explained (understand_bugs)
6. Common Patterns (common_patterns)

Or run individual functions from the Python REPL:
  >>> from QUICK_START import *
  >>> example_road_trip()
  >>> understand_cost_calculation()
  >>> debug_example()
  >>> etc.
    """)
    
    # Run one example to show it works
    print("\n" + "="*60)
    print("Running example_road_trip()...")
    print("="*60)
    example_road_trip()
    
    print("\n" + "="*60)
    print("Try running other functions!")
    print("="*60)


if __name__ == "__main__":
    main()
    
    # Uncomment to run specific examples:
    # example_road_trip()
    # understand_cost_calculation()
    # debug_example()
    # understand_bugs()
    # common_patterns()
    # run_tests()
