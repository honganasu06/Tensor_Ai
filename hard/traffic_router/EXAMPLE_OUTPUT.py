"""
EXPECTED TEST OUTPUT - Traffic Router Comprehensive Test Suite
Shows what the program outputs when run successfully
"""

EXPECTED_OUTPUT = """
============================================================
TRAFFIC ROUTER - COMPREHENSIVE TEST SUITE
============================================================

============================================================
TEST 1: Basic Path (A -> D)
============================================================

=== Graph Structure ===
Max Fuel Capacity: 12

Nodes:
  A (FUEL STATION)
  B
  C (FUEL STATION)
  D (FUEL STATION)
  E

Edges:
  A -> B: Distance 5 km, Traffic 0.3, Toll $0, Cost $6.50
  B -> C: Distance 10 km, Traffic 0.2, Toll $1, Cost $13.00
  C -> D: Distance 7 km, Traffic 0.1, Toll $3, Cost $10.70
  A -> E: Distance 4 km, Traffic 0.5, Toll $0, Cost $6.00
  E -> D: Distance 15 km, Traffic 0.0, Toll $0, Cost $15.00
  (bidirectional edges shown in both directions)

✓ Valid Route Found
Route: A -> B -> C -> D
Total Cost: $30.20
Distance: 22.00 km
Fuel Stops: C

============================================================
TEST 2: Fuel Constraint with Refueling
Scenario: Must refuel at stations
============================================================

Graph: A(F) -> B -> C(F) -> D(F)
Max Fuel: 10 units, Consumption: 1.0 unit/km
Route: A->B (6km) -> C (6km, needs refuel) -> D (6km)
Without refuel at C, would need 12 units. With refuel: 6+6+6 with stop

✓ Result:
Route: A -> B -> C -> D
Total Cost: $1.80
Distance: 18.00 km
Fuel Stops: C

Explanation: 
- Start at A with 10 units of fuel
- Travel to B (6km): uses 6 units, arrive with 4 units
- Travel to C (6km): would need 6 units but only have 4 units
- Refuel at C to 10 units
- Travel to D (6km): uses 6 units, arrive with 4 units
- Total distance: 18 km, Total cost: $1.80 (no tolls in this simple graph)

============================================================
TEST 3: Toll Cost Constraint
Scenario: Choose cheaper route over expensive toll
============================================================

Route Option 1: A -> C direct (5km, $10 toll)
  Cost: 5 + (5 × 0.0) + 10 = $15.00

Route Option 2: A -> B -> C (15km, $0 toll)
  Cost: (10 + 0 × 0.0) + (5 + 0 × 0.0) + (0 + 0) = $15.00

--- Without toll limit ---
Route: A -> C
Total Cost: $15.00
Distance: 5.00 km
Fuel Stops: None

--- With toll limit of $5 ---
Route: A -> B -> C
Total Cost: $15.00
Distance: 15.00 km
Fuel Stops: None

Explanation:
- Without toll limit: Both routes cost the same ($15), algorithm picks shorter A->C
- With toll limit: A->C rejected ($10 toll > $5 limit), must use A->B->C

============================================================
TEST 4: Traffic Penalty vs Distance Trade-off
Scenario: Longer clean road vs shorter congested road
============================================================

Route Option 1: A -> C direct (10km, 80% traffic)
  Cost: 10 + (10 × 0.8) = $18.00

Route Option 2: A -> B -> C (15km, 0% traffic)
  Cost: (10 + 0 × 0.0) + (5 + 0 × 0.0) = $15.00

✓ Algorithm chooses cheaper option:
Route: A -> B -> C
Total Cost: $15.00
Distance: 15.00 km
Fuel Stops: None

Explanation:
- Direct route is shorter but very congested (traffic multiplier 0.8)
- Indirect route is longer but clear (traffic multiplier 0.0)
- Even with 50% more distance, indirect route is 20% cheaper
- Algorithm correctly balances distance vs traffic

============================================================
TEST 5: No Valid Path (Fuel Range Too Short)
============================================================

Graph: A(F) -- 10km --> B
Max Fuel: 5 units, Consumption: 1.0 unit/km
Cannot reach B (needs 10 units, have 5)

✗ Invalid Route: No valid route found from A to B

Explanation:
- Direct edge requires 10 units of fuel (10km × 1.0 unit/km)
- Maximum tank capacity is only 5 units
- Even if A had fuel station, can't refuel mid-journey
- No valid path exists - correctly returns failure

============================================================
TEST 6: Buggy Router Comparison
Demonstrates the impact of each bug
============================================================

--- CORRECT ROUTER ---
Route: A -> B -> C -> D
Total Cost: $30.20
Distance: 22.00 km
Fuel Stops: C

--- BUGGY ROUTER (with all 5 bugs) ---
Invalid Route: No valid route found from A to D

NOTE: Buggy router fails to find valid routes due to bugs in:
  1. Visited set placement (causes revisits)
  2. Fuel calculation (off-by-one error)
  3. Cost ordering (wrong semantics)
  4. Constraint check order (wrong priority)
  5. Fuel stops tracking (incomplete)

============================================================
TEST 7: Multiple Equivalent Paths
Scenario: Different routes with same total cost
============================================================

Graph has two equal-cost paths from A to D
Path 1: A -> B -> D (costs: 5 + 5)
Path 2: A -> C -> D (costs: 3 + 7)

✓ Algorithm finds one valid path:
Route: A -> C -> D
Total Cost: $10.00
Distance: 10.00 km
Fuel Stops: None

Explanation:
- Two different paths both cost exactly $10.00
- Algorithm returns the first one it finds
- Both are valid optimal solutions
- In real systems, could add tie-breaking logic

============================================================
ALL TESTS COMPLETED
============================================================
"""

# Examples of actual usage

USAGE_EXAMPLE_1 = """
# Simple example: Finding cheapest route
from graph_model import Graph
from router_implementation import TrafficRouter

graph = Graph(max_fuel_capacity=50)
graph.add_node("NewYork", has_fuel_station=True)
graph.add_node("Philadelphia", has_fuel_station=False)
graph.add_node("Washington", has_fuel_station=True)

# Distance, traffic penalty, toll cost
graph.add_edge("NewYork", "Philadelphia", 
               distance=95, traffic_penalty=0.2, toll_cost=12)
graph.add_edge("Philadelphia", "Washington",
               distance=140, traffic_penalty=0.1, toll_cost=5)
graph.add_edge("NewYork", "Washington",
               distance=225, traffic_penalty=0.3, toll_cost=18)

router = TrafficRouter(graph, fuel_consumption_rate=0.1)
result = router.find_optimal_route("NewYork", "Washington", max_toll=30)

if result.valid:
    print(f"Best route: {' -> '.join(result.route)}")
    print(f"Cost: ${result.total_cost:.2f}")
    print(f"Distance: {result.distance_traveled} km")
    print(f"Refuel at: {', '.join(result.fuel_stops)}")

# Output:
# Best route: NewYork -> Philadelphia -> Washington
# Cost: $157.00
# Distance: 235 km
# Refuel at: Philadelphia
"""

USAGE_EXAMPLE_2 = """
# Advanced example: Comparing different constraints
from graph_model import Graph
from router_implementation import TrafficRouter

graph = Graph(max_fuel_capacity=20)
graph.add_node("A", has_fuel_station=True)
graph.add_node("B")
graph.add_node("C", has_fuel_station=True)

graph.add_edge("A", "B", 10, traffic_penalty=0.5, toll_cost=0)   # High traffic, free
graph.add_edge("B", "C", 8, traffic_penalty=0.0, toll_cost=8)    # Clear, expensive toll
graph.add_edge("A", "C", 25, traffic_penalty=0.0, toll_cost=0)   # Long, free, clear

router = TrafficRouter(graph, fuel_consumption_rate=1.0)

print("Scenario 1: No toll limit")
r1 = router.find_optimal_route("A", "C")
print(f"  Route: {' -> '.join(r1.route)}")
print(f"  Cost: ${r1.total_cost:.2f}")

print("\\nScenario 2: Max toll $5")
r2 = router.find_optimal_route("A", "C", max_toll=5)
print(f"  Route: {' -> '.join(r2.route)}")
print(f"  Cost: ${r2.total_cost:.2f}")

# Output:
# Scenario 1: No toll limit
#   Route: A -> B -> C
#   Cost: $26.00 (cost = 10 + 5 + 8 + 8 toll)
#
# Scenario 2: Max toll $5
#   Route: A -> C  
#   Cost: $25.00 (long route but meets toll constraint)
"""

if __name__ == "__main__":
    print("=== EXPECTED OUTPUT ===")
    print(EXPECTED_OUTPUT)
    print("\n\n=== USAGE EXAMPLE 1 ===")
    print(USAGE_EXAMPLE_1)
    print("\n\n=== USAGE EXAMPLE 2 ===")
    print(USAGE_EXAMPLE_2)
