from __future__ import annotations
from math import sqrt
import numpy as np
from plotHelper import getPlot
from random import randint
from multiprocessing import Pool
from time import sleep, time
import threading
import matplotlib.pyplot as plt
import concurrent.futures

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

    def __str__(self):
        return f"Seed({self.id}, {self.x}, {self.y})"

    def __repr__(self):
        return f"Seed({self.id}, {self.x}, {self.y})"

# get random different seeds


def getRandomSeeds(n: int, k: int) -> list[Seed]:
    seeds = []
    for i in range(k):
        while True:
            x = randint(0, n - 1)
            y = randint(0, n - 1)
            seed = Seed(i, x, y)
            if seed not in seeds:
                seeds.append(seed)
                break
    return seeds

# transform list of tuples into list of seeds


def getSeeds(seeds: list[tuple[int, int]]) -> list[Seed]:
    return [Seed(i+1, x, y) for i, (x, y) in enumerate(seeds)]


class VoronoiDiagram:
    n: int
    seeds: list[Seed]
    matrix: np.ndarray
    i : int

    def __init__(self, n: int, seeds: list[Seed]):
        self.i = 1
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
    def getDiagramHelperThreaded(self, corners: list[tuple[int, int]]):
        #print name of current thread
        # calculate the closest seed to each corner
        closestSeed = []
        # getPlot(self.matrix, self.seeds)
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

            if self.i == 1:
                self.i += 1

                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    executor.map(self.getDiagramHelperThreaded, [firstQuadrant, secondQuadrant, thirdQuadrant, fourthQuadrant])

                # first = threading.Thread(name = 'firstQuadrant', target= self.getDiagramHelperThreaded, args=(firstQuadrant,), daemon= False)
                # second = threading.Thread(name = 'secondQuadrant', target= self.getDiagramHelperThreaded, args=(secondQuadrant,), daemon= False)
                # third = threading.Thread(name = 'thirdQuadrant', target= self.getDiagramHelperThreaded, args=(thirdQuadrant,), daemon=False)
                # fourth = threading.Thread(name = 'fourthQuadrant', target= self.getDiagramHelperThreaded, args=(fourthQuadrant,), daemon= False)

                # first.start()
                # second.start()
                # third.start()
                # fourth.start()

                # first.join()
                # second.join()
                # third.join()
                # fourth.join()

            else:
                self.getDiagramHelperThreaded(firstQuadrant)
                self.getDiagramHelperThreaded(secondQuadrant)
                self.getDiagramHelperThreaded(thirdQuadrant)
                self.getDiagramHelperThreaded(fourthQuadrant)

    def getDiagramHelperNonThreaded(self, corners: list[tuple[int, int]]):
        # calculate the closest seed to each corner
        closestSeed = []
        # getPlot(self.matrix, self.seeds)
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

            self.getDiagramHelperThreaded(firstQuadrant)
            self.getDiagramHelperThreaded(secondQuadrant)
            self.getDiagramHelperThreaded(thirdQuadrant)
            self.getDiagramHelperThreaded(fourthQuadrant)


if __name__ == "__main__":
    # define seeds
    # define matrix
    n = 2 ** 6
    seeds = getRandomSeeds(n, 50)
    # seeds = getSeeds([(938, 730), (826, 423), (193, 178), (862, 414), (121, 937), (0, 798), (583, 190), (610, 247), (345, 350), (126, 872), (828, 213), (73, 388), (918, 580), (349, 516), (1014, 603), (229, 972), (987, 324), (618, 424), (843, 555), (131, 449), (370, 556), (883, 800), (946, 439), (486, 723), (896, 322), (132, 194), (624, 507), (746, 934), (899, 284), (948, 993), (999, 378), (893, 168), (647, 1017), (468, 108), (472, 676), (76, 423), (851, 410), (452, 9), (108, 325), (86, 899), (1008, 635), (389, 121), (161, 709), (331, 799), (321, 997), (915, 604), (490, 780), (483, 253), (591, 979), (760, 780), (946, 824), (817, 685), (155, 316), (293, 557), (185, 203), (148, 813), (992, 725), (727, 539), (765, 814), (876, 27), (638, 681), (500, 564), (906, 297), (434, 352), (287, 338), (247, 520), (551, 627), (732, 577), (748, 234), (105, 607), (373, 301), (54, 655), (408, 806), (719, 998), (607, 290), (382, 29), (918, 315), (702, 296), (141, 417), (1018, 212), (980, 294), (424, 399), (113, 800), (863, 58), (503, 804), (19, 467), (582, 76), (342, 552), (1018, 418), (781, 935), (40, 457), (107, 516), (63, 697), (344, 916), (992, 1017), (605, 853), (700, 99), (759, 752), (17, 716), (613, 409)])
    # seeds = getSeeds([(938, 730), (826, 423), (193, 178), (862, 414), (121, 937), (0, 798), (583, 190), (610, 247), (345, 350), (126, 872), (828, 213), (73, 388), (918, 580), (349, 516), (1014, 603), (229, 972), (987, 324), (618, 424), (843, 555), (131, 449), (370, 556), (883, 800), (946, 439), (486, 723), (896, 322), (132, 194), (624, 507), (746, 934), (899, 284), (948, 993), (999, 378), (893, 168), (647, 1017), (468, 108), (472, 676), (76, 423), (851, 410), (452, 9), (108, 325), (86, 899), (1008, 635), (389, 121), (161, 709), (331, 799), (321, 997), (915, 604), (490, 780), (483, 253), (591, 979), (760, 780), (946, 824), (817, 685), (155, 316), (293, 557), (185, 203), (148, 813), (992, 725), (727, 539), (765, 814), (876, 27), (638, 681), (500, 564), (906, 297), (434, 352), (287, 338), (247, 520), (551, 627)])

    voronoiDiagram = VoronoiDiagram(n, seeds)
    # measure time
    start = time()
    voronoiDiagram.getDiagramHelperThreaded(
        [(0, 0), (n - 1, 0), (n - 1, n - 1), (0, n - 1)])
    end = time()
    print("Time threaded: ", end - start)

    print(voronoiDiagram.matrix)

    # del voronoiDiagram

    voronoiDiagram2 = VoronoiDiagram(n, seeds)
    # measure time
    start = time()
    voronoiDiagram2.getDiagramHelperNonThreaded(
        [(0, 0), (n - 1, 0), (n - 1, n - 1), (0, n - 1)])
    end = time()
    print("Time non threaded: ", end - start)

    print(voronoiDiagram2.matrix)

    # getPlot(voronoiDiagram.matrix, voronoiDiagram.seeds)

    # plt.imshow(voronoiDiagram.matrix, cmap='hot', interpolation='nearest')
    # plt.show()
    # print(voronoiDiagram.matrix)
