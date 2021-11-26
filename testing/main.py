import os
from time import time
from ctypes import CDLL, POINTER, c_uint16, c_int

def test(seeds):
    MAX_SEEDS = len(seeds)
    CVoronoi  = CDLL(os.path.abspath("voronoi_2048.so"))
    voronoi = CVoronoi.voronoi_2048
    voronoi.argtypes = [POINTER(c_uint16), POINTER(c_int), POINTER(c_int), c_int, c_int]
    MATRIX_L = 2048 #Don't change 2048

    matrix = (c_uint16*(MATRIX_L*MATRIX_L))()
    seeds_x = (c_int*MAX_SEEDS)()
    seeds_y = (c_int*MAX_SEEDS)()
    n_seeds = c_int(MAX_SEEDS)
    threaded = 1

    for i in range(MAX_SEEDS):
        seeds_x[i] = c_int(seeds[i][0])
        seeds_y[i] = c_int(seeds[i][1])

    start = time()
    voronoi(matrix, seeds_x, seeds_y, n_seeds, threaded)
    end = time()

    return end-start
