import unittest
from utils.recursiveWalk import (
    recursiveWalk,
    recursiveWalk2,
    EMPTY,
    VISITED,
    ENDING,
    WALL,
)
import time


def printMatrix(matrix):
    print("\n")
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(matrix[i][j], end=" ")
        print()
    print("\n")


maze = [
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
]


class TestRecursiveWalk(unittest.TestCase):
    global maze
    startingPoint: list[int]
    endingPoint: list[int]
    matrixRows = len(maze)
    matrixCols = len(maze[0])

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        for i in range(self.matrixRows):
            if maze[0][i] == EMPTY:
                self.startingPoint = [0, i]
                break

        for i in range(self.matrixRows):
            if maze[self.matrixRows - 1][i] == EMPTY:
                self.endingPoint = [self.matrixRows - 1, i]
                break
        print(f"Starting: {self.startingPoint} Ending: {self.endingPoint}")

    def test_recursiveWalk(self):

        maze[self.endingPoint[0]][self.endingPoint[1]] = 2
        printMatrix(maze)

        path = recursiveWalk(maze, self.startingPoint[0], self.startingPoint[1])
        printMatrix(path)

        time.sleep(1)
        self.assertIsNotNone(path)

    def test_recursiveWalk2(self):
        maze[self.endingPoint[0]][self.endingPoint[1]] = ENDING

        path = recursiveWalk2(maze, self.startingPoint[0], self.startingPoint[1])
        printMatrix(path)

        time.sleep(1)
        self.assertIsNotNone(path)
