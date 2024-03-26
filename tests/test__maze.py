import unittest
from utils.maze import create_maze


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
        self.assertIsNotNone(maze)
