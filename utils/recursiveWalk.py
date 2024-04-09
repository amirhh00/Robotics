import os
import random
import sys
import time

EMPTY = 0
WALL = 1
ENDING = 2
VISITED = 3
UNVISITED = float("inf")


def recursiveWalk(grid, x, y):
    print("\n")

    def search(x, y):
        if grid[x][y] == ENDING:
            # print("found at %d,%d" % (x, y))
            return True
        elif grid[x][y] == WALL:
            # print("wall at %d,%d" % (x, y))
            return False
        elif grid[x][y] == VISITED:
            print("visited at %d,%d" % (x, y))
            return False
        print("-Visiting- %d,%d" % (x, y))
        # mark as visited
        grid[x][y] = VISITED

        # explore neighbors clockwise starting by the one on the right
        if (
            (x < len(grid) - 1 and search(x + 1, y))
            or (y > 0 and search(x, y - 1))
            or (x > 0 and search(x - 1, y))
            or (y < len(grid) - 1 and search(x, y + 1))
        ):
            return True
        return False

    search(x, y)
    return grid


didFind = False


class SolutionFoundException(Exception):
    pass


def recursiveWalk2(maze, x, y):
    print("\n")

    def move(path):
        time.sleep(0.2)
        global didFind
        if didFind:
            return
        cur = path[-1]
        print(f"Visiting {cur}")
        possibles = [
            (cur[0], cur[1] + 1),
            (cur[0], cur[1] - 1),
            (cur[0] + 1, cur[1]),
            (cur[0] - 1, cur[1]),
        ]
        random.shuffle(possibles)
        for item in possibles:
            if (
                item[0] < 0
                or item[1] < 0
                or item[0] > len(maze)
                or item[1] > len(maze[0])
            ):
                continue
            elif maze[item[0]][item[1]] in [WALL, VISITED]:
                continue
            elif item in path:
                continue
            elif maze[item[0]][item[1]] == ENDING:
                path = path + (item,)
                print(f"Visiting {item}")
                print("Solution found! Press enter to finish")
                didFind = True
                return
            else:
                # print(f"Visiting {item}")
                newpath = path + (item,)
                time.sleep(0.2)
                move(newpath)
                maze[item[0]][item[1]] = VISITED
        return maze

    return move(((x, y),))
