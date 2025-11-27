"""
wumpus_world.py

Competition-ready A* implementation for a grid-based Wumpus world.
Class: WumpusWorld
Method expected by validator: search()

- Grid representation:
    0 -> free cell
    1 -> obstacle / hazard (impassable)
- start, goal: (row, col) or list-like [row, col]

Behavior:
- If start==goal and start is valid, returns [start].
- If no path exists, returns None.
- Never raises an exception for normal/malformed inputs; returns None if inputs invalid.
"""

import heapq
from typing import List, Tuple, Optional

Coord = Tuple[int, int]

class WumpusWorld:
    def __init__(self, grid: List[List[int]], start, goal):
        # Normalize types and perform validation but do not raise - return None later in search if invalid
        self.grid = grid if isinstance(grid, list) and grid else []
        self.start = tuple(start) if (isinstance(start, (list, tuple)) and len(start) == 2) else None
        self.goal = tuple(goal) if (isinstance(goal, (list, tuple)) and len(goal) == 2) else None

        # Dimensions (safe fallback)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 and isinstance(self.grid[0], list) else 0

    def heuristic(self, a: Coord, b: Coord) -> int:
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def in_bounds(self, node: Coord) -> bool:
        r, c = node
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_free(self, node: Coord) -> bool:
        # Treat anything not exactly 1 as free (defensive)
        r, c = node
        try:
            return self.grid[r][c] != 1
        except Exception:
            return False

    def get_neighbors(self, node: Coord) -> List[Coord]:
        # 4-connected grid
        r, c = node
        candidates = [(r+1,c), (r-1,c), (r,c+1), (r,c-1)]
        neighbors = []
        for n in candidates:
            if self.in_bounds(n) and self.is_free(n):
                neighbors.append(n)
        return neighbors

    def reconstruct(self, came_from: dict, end: Coord) -> List[Coord]:
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = came_from.get(node)
        path.reverse()
        return path

    # Public method expected by validator
    def search(self) -> Optional[List[Coord]]:
        # Validate grid presence
        if self.rows == 0 or self.cols == 0:
            # invalid grid
            return None

        # Validate start/goal
        if self.start is None or self.goal is None:
            return None
        if not (self.in_bounds(self.start) and self.in_bounds(self.goal)):
            return None

        # Make sure start and goal are free cells
        if not self.is_free(self.start) or not self.is_free(self.goal):
            return None

        # Trivial case
        if self.start == self.goal:
            return [self.start]

        # A* initialization
        open_heap = []
        heapq.heappush(open_heap, (0 + self.heuristic(self.start, self.goal), 0, self.start))
        came_from = { self.start: None }
        g_score = { self.start: 0 }
        closed = set()

        while open_heap:
            f, g, current = heapq.heappop(open_heap)

            # If we've already processed this node with a better g, skip
            if g_score.get(current, float('inf')) < g:
                continue

            if current == self.goal:
                return self.reconstruct(came_from, current)

            closed.add(current)

            for nb in self.get_neighbors(current):
                if nb in closed:
                    continue

                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(nb, float('inf')):
                    came_from[nb] = current
                    g_score[nb] = tentative_g
                    f_score = tentative_g + self.heuristic(nb, self.goal)
                    heapq.heappush(open_heap, (f_score, tentative_g, nb))

        # No path found
        return None


# If someone runs this file directly, show a tiny self-test (safe)
if __name__ == "__main__":
    simple_grid = [
        [0,0,0],
        [0,1,0],
        [0,0,0]
    ]
    ww = WumpusWorld(simple_grid, (0,0), (2,2))
    p = ww.search()
    print("Self-test path:", p)
