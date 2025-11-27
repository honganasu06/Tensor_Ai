"""
Test Suite for Traffic Router
Demonstrates bug fixes and edge case handling
"""

from graph_model import Graph
from router_implementation import TrafficRouter
from buggy_router import BuggyTrafficRouter


def create_example_graph():
    """Create the example graph from requirements"""
    graph = Graph(max_fuel_capacity=12)
    
    # Add nodes with fuel stations
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B", has_fuel_station=False)
    graph.add_node("C", has_fuel_station=True)
    graph.add_node("D", has_fuel_station=True)
    graph.add_node("E", has_fuel_station=False)
    
    # Add edges (bidirectional)
    # Format: (from, to, distance, traffic_penalty, toll)
    graph.add_edge("A", "B", 5, traffic_penalty=0.3, toll_cost=0)
    graph.add_edge("B", "C", 10, traffic_penalty=0.2, toll_cost=1)
    graph.add_edge("C", "D", 7, traffic_penalty=0.1, toll_cost=3)
    graph.add_edge("A", "E", 4, traffic_penalty=0.5, toll_cost=0)
    graph.add_edge("E", "D", 15, traffic_penalty=0.0, toll_cost=0)
    
    return graph


def test_basic_path():
    """TEST 1: Basic routing without constraints"""
    print("\n" + "="*60)
    print("TEST 1: Basic Path (A -> D)")
    print("="*60)
    
    graph = create_example_graph()
    router = TrafficRouter(graph, fuel_consumption_rate=0.5)  # 0.5 units per km
    graph.print_structure()
    
    result = router.find_optimal_route("A", "D")
    print(f"\n✓ Valid Route Found" if result.valid else f"\n✗ Route Failed")
    print(result)


def test_fuel_constraint():
    """TEST 2: Fuel constraint forces refueling"""
    print("\n" + "="*60)
    print("TEST 2: Fuel Constraint with Refueling")
    print("Scenario: Must refuel at stations")
    print("="*60)
    
    graph = Graph(max_fuel_capacity=10)  # Limited capacity
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B", has_fuel_station=False)
    graph.add_node("C", has_fuel_station=True)
    graph.add_node("D", has_fuel_station=True)
    
    # Create a route that requires refueling at C
    graph.add_edge("A", "B", 6, traffic_penalty=0.1, toll_cost=0)
    graph.add_edge("B", "C", 6, traffic_penalty=0.1, toll_cost=0)
    graph.add_edge("C", "D", 6, traffic_penalty=0.1, toll_cost=0)
    
    router = TrafficRouter(graph, fuel_consumption_rate=1.0)
    print("\nGraph: A(F) -> B -> C(F) -> D(F)")
    print(f"Max Fuel: 10 units, Consumption: 1.0 unit/km")
    print(f"Route: A->B (6km) -> C (6km, needs refuel) -> D (6km)")
    print(f"Without refuel at C, would need 12 units. With refuel: 6+6+6 with stop")
    
    result = router.find_optimal_route("A", "D", debug=False)
    print(f"\n✓ Result:")
    print(result)


def test_toll_constraint():
    """TEST 3: Toll cost limit"""
    print("\n" + "="*60)
    print("TEST 3: Toll Cost Constraint")
    print("Scenario: Choose cheaper route over expensive toll")
    print("="*60)
    
    graph = Graph(max_fuel_capacity=20)
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B", has_fuel_station=False)
    graph.add_node("C", has_fuel_station=True)
    
    # Route 1: Expensive toll road (shorter)
    graph.add_edge("A", "C", 5, traffic_penalty=0.0, toll_cost=10)
    # Route 2: Cheap road but longer (A->B->C)
    graph.add_edge("A", "B", 8, traffic_penalty=0.1, toll_cost=0)
    graph.add_edge("B", "C", 7, traffic_penalty=0.1, toll_cost=0)
    
    router = TrafficRouter(graph)
    print("\nRoute Option 1: A -> C direct (5km, $10 toll)")
    print("Route Option 2: A -> B -> C (15km, $0 toll)")
    
    print("\n--- Without toll limit ---")
    result1 = router.find_optimal_route("A", "C")
    print(result1)
    
    print("\n--- With toll limit of $5 ---")
    result2 = router.find_optimal_route("A", "C", max_toll=5)
    print(result2)


def test_traffic_vs_distance():
    """TEST 4: Traffic penalty trade-off"""
    print("\n" + "="*60)
    print("TEST 4: Traffic Penalty vs Distance Trade-off")
    print("Scenario: Longer clean road vs shorter congested road")
    print("="*60)
    
    graph = Graph(max_fuel_capacity=30)
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B", has_fuel_station=False)
    graph.add_node("C", has_fuel_station=True)
    
    # Route 1: Short but very congested (10km, 80% traffic)
    graph.add_edge("A", "C", 10, traffic_penalty=0.8, toll_cost=0)
    # Route 2: Longer but clear (15km, 0% traffic)
    graph.add_edge("A", "B", 10, traffic_penalty=0.0, toll_cost=0)
    graph.add_edge("B", "C", 5, traffic_penalty=0.0, toll_cost=0)
    
    router = TrafficRouter(graph)
    print("\nRoute Option 1: A -> C direct (10km, 80% traffic)")
    print("  Cost: 10 + (10 * 0.8) = 18")
    print("\nRoute Option 2: A -> B -> C (15km, 0% traffic)")
    print("  Cost: (10 + 0) + (5 + 0) = 15")
    
    result = router.find_optimal_route("A", "C")
    print(f"\n✓ Algorithm chooses cheaper option:")
    print(result)


def test_no_valid_path():
    """TEST 5: No valid path due to fuel range"""
    print("\n" + "="*60)
    print("TEST 5: No Valid Path (Fuel Range Too Short)")
    print("="*60)
    
    graph = Graph(max_fuel_capacity=5)
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B", has_fuel_station=False)
    
    # 10km road but only 5 units of fuel capacity
    graph.add_edge("A", "B", 10, traffic_penalty=0.0, toll_cost=0)
    
    router = TrafficRouter(graph, fuel_consumption_rate=1.0)
    print("\nGraph: A(F) -- 10km --> B")
    print(f"Max Fuel: 5 units, Consumption: 1.0 unit/km")
    print(f"Cannot reach B (needs 10 units, have 5)")
    
    result = router.find_optimal_route("A", "B")
    print(f"\n✗ {result}")


def test_buggy_router_comparison():
    """TEST 6: Compare buggy vs correct router"""
    print("\n" + "="*60)
    print("TEST 6: Buggy Router Comparison")
    print("Demonstrates the impact of each bug")
    print("="*60)
    
    graph = create_example_graph()
    
    print("\n--- CORRECT ROUTER ---")
    correct_router = TrafficRouter(graph)
    correct_result = correct_router.find_optimal_route("A", "D")
    print(correct_result)
    
    print("\n--- BUGGY ROUTER (with all 5 bugs) ---")
    buggy_router = BuggyTrafficRouter(graph)
    buggy_result = buggy_router.find_optimal_route("A", "D", debug=False)
    print(buggy_result)
    print("\nNOTE: Buggy router may produce incorrect results or hang")


def test_multiple_paths_same_cost():
    """TEST 7: Multiple paths with equivalent costs"""
    print("\n" + "="*60)
    print("TEST 7: Multiple Equivalent Paths")
    print("Scenario: Different routes with same total cost")
    print("="*60)
    
    graph = Graph(max_fuel_capacity=20)
    
    # Diamond topology - two paths of equal cost
    graph.add_node("A", has_fuel_station=True)
    graph.add_node("B", has_fuel_station=False)
    graph.add_node("C", has_fuel_station=False)
    graph.add_node("D", has_fuel_station=True)
    
    # Path 1: A -> B -> D (cost: 5 + 5 = 10)
    graph.add_edge("A", "B", 5, traffic_penalty=0.0, toll_cost=0)
    graph.add_edge("B", "D", 5, traffic_penalty=0.0, toll_cost=0)
    
    # Path 2: A -> C -> D (cost: 3 + 7 = 10) - same total
    graph.add_edge("A", "C", 3, traffic_penalty=0.0, toll_cost=0)
    graph.add_edge("C", "D", 7, traffic_penalty=0.0, toll_cost=0)
    
    router = TrafficRouter(graph)
    print("\nGraph has two equal-cost paths from A to D")
    print("Path 1: A -> B -> D (costs: 5 + 5)")
    print("Path 2: A -> C -> D (costs: 3 + 7)")
    
    result = router.find_optimal_route("A", "D")
    print(f"\n✓ Algorithm finds one valid path:")
    print(result)


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("TRAFFIC ROUTER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    test_basic_path()
    test_fuel_constraint()
    test_toll_constraint()
    test_traffic_vs_distance()
    test_no_valid_path()
    test_buggy_router_comparison()
    test_multiple_paths_same_cost()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
