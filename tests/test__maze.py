import unittest
from utils.maze import create_maze
import time


class TestMaze(unittest.TestCase):
    def test_maze(self):
        matrixRows = 10
        matrixCols = 10
        maze = create_maze(matrixRows, matrixCols)
        print("Maze:\n")
        for i in range(matrixRows):
            for j in range(matrixCols):
                print(maze[i][j], end=" ")
            print()

        print("\n")
        time.sleep(0.1)
        self.assertIsNotNone(maze)
