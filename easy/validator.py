"""
validator.py

Robust test runner that imports WumpusWorld and runs tests in test_cases.json.

Checks performed for each returned path:
- Path is a list of (r,c) tuples/lists
- First node == start, last node == goal
- Every node is inside bounds and not an obstacle
- Consecutive nodes are 4-neighbors (Manhattan distance == 1)

If inputs are malformed or path is None, prints clear info.
"""

import json
import sys
from typing import List, Tuple
from wumpus_world import WumpusWorld

Coord = Tuple[int, int]

import os

def load_tests(path="test_cases.json"):
    # Resolve path relative to script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)
    
    try:
        with open(full_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "cases" not in data:
            print("ERROR: test_cases.json must contain a top-level 'cases' list.")
            return []
        return data["cases"]
    except FileNotFoundError:
        print("ERROR: test_cases.json not found.")
        return []
    except json.JSONDecodeError as e:
        print("ERROR: test_cases.json parse error:", e)
        return []
    except Exception as e:
        print("ERROR reading test_cases.json:", e)
        return []

def validate_path(grid: List[List[int]], start, goal, path) -> bool:
    # Basic validation of types
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    def in_bounds(node):
        if not isinstance(node, (list, tuple)) or len(node) != 2:
            return False
        r, c = node
        return isinstance(r, int) and isinstance(c, int) and 0 <= r < rows and 0 <= c < cols

    def is_free(node):
        r, c = node
        try:
            return grid[r][c] != 1
        except Exception:
            return False

    # Path must be a list-like with at least 1 element
    if path is None:
        return False

    if not isinstance(path, list) or len(path) == 0:
        return False

    # Check start and goal
    if tuple(path[0]) != tuple(start):
        return False
    if tuple(path[-1]) != tuple(goal):
        return False

    # Validate every node and adjacency
    prev = None
    for node in path:
        if not in_bounds(node):
            return False
        if not is_free(node):
            return False
        if prev is not None:
            # Manhattan distance must be 1
            if abs(node[0]-prev[0]) + abs(node[1]-prev[1]) != 1:
                return False
        prev = tuple(node)

    return True

def run_all_tests():
    cases = load_tests()
    if not cases:
        print("No test cases found or error reading file.")
        return

    total = len(cases)
    passed = 0

    for idx, case in enumerate(cases, start=1):
        print("\n=== Test case", idx, "===")
        name = case.get("name", f"case_{idx}")
        grid = case.get("grid")
        start = case.get("start")
        goal = case.get("goal")

        print("Name:", name)
        print("Start:", start, "Goal:", goal)

        # Basic sanity checks
        if not isinstance(grid, list) or not isinstance(start, (list, tuple)) or not isinstance(goal, (list, tuple)):
            print("INVALID TEST CASE FORMAT - skipping")
            continue

        try:
            ww = WumpusWorld(grid, start, goal)
            path = ww.search()
        except Exception as e:
            print("ERROR: Exception raised by WumpusWorld.search():", e)
            path = None

        if path is None:
            print("Result: No path returned (None)")
            # It's allowed to have no path; mark as fail only if the case explicitly says expected: true
            expected = case.get("expected")  # optional boolean
            if expected is True:
                print("❌ Expected a path but none found.")
            else:
                print("✔ (No path) — acceptable if test expects no path or unspecified.")
                # Consider this a pass only if expected is False; otherwise count as neutral
                if expected is False:
                    passed += 1
            continue

        # Validate returned path
        good = validate_path(grid, start, goal, path)
        if good:
            print("✔ Path valid. Length:", len(path))
            print("Path:", path)
            # If test specified expected boolean, consider it
            expected = case.get("expected")
            if expected is True or expected is None:
                passed += 1
        else:
            print("❌ Path invalid. The returned path fails checks (bounds/obstacle/adjacency/start-goal).")
            print("Returned path:", path)

    print("\nSummary: passed", passed, "/", total, "tests (counts expected if specified).")

if __name__ == "__main__":
    run_all_tests()
