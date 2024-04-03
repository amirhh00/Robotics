import unittest
from utils.astar import astar


class TestAStar(unittest.TestCase):
    def test_astar(self):
        maze = [
            [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
            [0, 1, 1, 0, 0, 0, 1, 1, 0, 1],
            [0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
            [0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [0, 1, 1, 0, 1, 0, 1, 0, 0, 1],
            [0, 1, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        ]

        start = (0, 0)
        end = (9, 9)

        path = astar(maze, start, end)
        print("priint")
        print(path)

        # expect result to exists
        self.assertIsNotNone(path)


if __name__ == "__main__":
    unittest.main()
