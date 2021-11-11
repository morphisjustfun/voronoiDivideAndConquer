from __future__ import annotations
from math import sqrt
import numpy as np

# n is going to be the size of the square matrix
# seeds are going to be the seeds of the matrix (voronoi)


class Seed:
    id: int
    x: int
    y: int

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Value of seed not supported")

    def __eq__(self, other: Seed):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def distance(self, point: tuple[int, int]) -> float:
        return sqrt((self[0] - point[0])**2 + (self[1] - point[1])**2)


class VoronoiDiagram:
    n: int
    seeds: list[Seed]
    matrix: np.ndarray

    def __init__(self, n: int, seeds: list[Seed]):
        self.n = n
        self.seeds = seeds
        self.matrix = np.full((n, n), -1)

        for seed in self.seeds:
            if seed[0] < 0 or seed[0] >= self.n or seed[1] < 0 or seed[1] >= self.n:
                raise ValueError("Seed is not in the matrix")

        for seed in self.seeds:
            self.matrix[seed[0]][seed[1]] = seed.id

    # corners must be in counterclockwise order and should begin with upper left corner
    # initial: [0,0] is the first corner
    # tuple[int,int] is the point (x, y)
    def getDiagramHelper(self, corners: list[tuple[int, int]]):
        # calculate the closest seed to each corner
        closestSeed = []
        for corner in corners:
            closestSeed.append(self.seeds[0])
            for seed in self.seeds:
                if seed.distance(corner) < closestSeed[-1].distance(corner):
                    closestSeed[-1] = seed

        if (len(set(closestSeed))) == 1:
            firstCorner = corners[0]
            secondCorner = corners[1]
            thirdCorner = corners[2]

            for height in range(firstCorner[0], secondCorner[0] + 1):
                for width in range(firstCorner[1], thirdCorner[1] + 1):
                    self.matrix[height][width] = closestSeed[0].id

        else:
            # get the corners of each quadrant
            firstQuadrant = []
            secondQuadrant = []
            thirdQuadrant = []
            fourthQuadrant = []

            # generate the corners of the uppper left quadrant
            firstQuadrant.append(corners[0])
            firstQuadrant.append(
                [corners[0][0] + (corners[1][0] - corners[0][0]) // 2, corners[0][1]])
            firstQuadrant.append([corners[0][0] +
                                  (corners[1][0] -
                                   corners[0][0]) //
                                  2, corners[0][1] +
                                  (corners[2][1] -
                                   corners[0][1]) //
                                  2])
            firstQuadrant.append(
                [corners[0][0], corners[0][1] + (corners[2][1] - corners[0][1]) // 2])
            # generate the corners of the lower left quadrant
            secondQuadrant.append(
                [corners[0][0] + (corners[1][0] - corners[0][0]) // 2 + 1, corners[0][1]])
            secondQuadrant.append(corners[1])
            secondQuadrant.append(
                [corners[1][0], corners[1][1] + (corners[2][1] - corners[1][1]) // 2])
            secondQuadrant.append([corners[0][0] +
                                   (corners[1][0] -
                                    corners[0][0]) //
                                   2 +
                                   1, corners[1][1] +
                                   (corners[2][1] -
                                    corners[1][1]) //
                                   2])
            # generate the corners of the lower right quadrant
            thirdQuadrant.append([corners[0][0] +
                                  (corners[1][0] -
                                   corners[0][0]) //
                                  2 +
                                  1, corners[0][1] +
                                  (corners[2][1] -
                                   corners[0][1]) //
                                  2 +
                                  1])
            thirdQuadrant.append(
                [corners[1][0], corners[1][1] + (corners[2][1] - corners[1][1]) // 2 + 1])
            thirdQuadrant.append(corners[2])
            thirdQuadrant.append(
                [corners[0][0] + (corners[1][0] - corners[0][0]) // 2 + 1, corners[2][1]])
            # generate the corners of the upper right quadrant
            fourthQuadrant.append(
                [corners[0][0], corners[0][1] + (corners[2][1] - corners[0][1]) // 2 + 1])
            fourthQuadrant.append([corners[0][0] +
                                   (corners[1][0] -
                                    corners[0][0]) //
                                   2, corners[0][1] +
                                   (corners[2][1] -
                                    corners[0][1]) //
                                   2 +
                                   1])
            fourthQuadrant.append(
                [corners[0][0] + (corners[1][0] - corners[0][0]) // 2, corners[2][1]])
            fourthQuadrant.append(corners[3])

            self.getDiagramHelper(firstQuadrant)
            self.getDiagramHelper(secondQuadrant)
            self.getDiagramHelper(thirdQuadrant)
            self.getDiagramHelper(fourthQuadrant)


if __name__ == "__main__":
    # define seeds
    seeds = []
    seeds.append(Seed(1, 1, 1))
    seeds.append(Seed(2, 7, 0))
    seeds.append(Seed(3, 6, 6))
    # define matrix
    n = 2 ** 13
    voronoiDiagram = VoronoiDiagram(n, seeds)
    voronoiDiagram.getDiagramHelper(
        [(0, 0), (n - 1, 0), (n - 1, n - 1), (0, n - 1)])
    print(voronoiDiagram.matrix)
