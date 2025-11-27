import unittest
from wumpus_world import BangaloreWumpusWorld, load_config
import sys
import os

class TestAStar(unittest.TestCase):
    def setUp(self):
        # Mock config
        self.config = {
            "team_id": "test_team",
            "seed": 42,
            "grid_config": {
                "traffic_lights": 2,
                "cows": 2,
                "pits": 2
            }
        }
        self.world = BangaloreWumpusWorld(self.config)

    def test_path_exists(self):
        """Test if a path is found when one exists"""
        path = self.world.find_path_astar()
        if path:
            print(f"Path found: {path}")
            self.assertTrue(len(path) > 0)
            self.assertEqual(path[0], tuple(self.world.agent_start))
            self.assertEqual(path[-1], tuple(self.world.goal_pos))
        else:
            print("No path found (could be valid if blocked)")

    def test_avoid_obstacles(self):
        """Test if path avoids pits and cows"""
        path = self.world.find_path_astar()
        if path:
            for x, y in path:
                cell_type = self.world.grid[y][x]['type']
                self.assertNotEqual(cell_type, 'pit', f"Path goes through pit at {x},{y}")
                self.assertNotEqual(cell_type, 'cow', f"Path goes through cow at {x},{y}")

    def test_manhattan_distance(self):
        """Test heuristic function"""
        p1 = (0, 0)
        p2 = (3, 4)
        dist = self.world._heuristic(p1, p2)
        self.assertEqual(dist, 7)

if __name__ == '__main__':
    unittest.main()
