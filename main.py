from ctypes import *
import os, random, pygame, sys, random
from dot import *

#Global DLL

CVoronoi  = CDLL(os.path.abspath("cMultithread/bridge.so"))
voronoi = CVoronoi.voronoi_L
voronoi.argtypes = [POINTER(c_uint16), POINTER(c_uint16), POINTER(c_int), POINTER(c_int), c_int, c_int]

#Global Constants
MATRIX_L = 512 #Don't change 512
MAX_SEEDS = 2000 #Realistic max (to avoid realloc)
N = 50
#Global Variables
#   you shouldn't define this inside a function (to avoid realloc)
matrix = (c_uint16*(MATRIX_L*MATRIX_L))()
matrix2 = (c_uint16*(MATRIX_L*MATRIX_L))()
seeds_x = (c_int*MAX_SEEDS)()
seeds_y = (c_int*MAX_SEEDS)()
n_seeds = 0 #This will be setted with set_seeds, dont change it manually
threaded = 1 # 1 yes, 0 no, you choose

#Global Function
#This will preprocess the coords, just in case
def setSeeds(X, Y): # X and Y are arrays
  xmax = max(X)
  ymax = max(Y)
  xmin = min(X)
  ymin = min(Y)
  REAL_L = max(xmax - xmin, ymax - ymin)
  global n_seeds 
  n_seeds = len(X)
  for i in range(n_seeds):
    seeds_x[i] = c_int(int(MATRIX_L*(X[i]-xmin)/REAL_L))
    seeds_y[i] = c_int(int(MATRIX_L*(Y[i]-ymin)/REAL_L))



def execute(seeds, threaded):
    X = []
    Y = []
    for seed in seeds:
        X.append(seed[0])
        Y.append(seed[1])
    setSeeds(X, Y)

    


# for j in range(MATRIX_L):
#     for i in range(MATRIX_L):
#         print(matrix[i*MATRIX_L + j], end=' ')

dots = []
for i in range(N):
    x = random.uniform(0, MATRIX_L)
    y = random.uniform(0, MATRIX_L)
    dots.append(Dot(x, y))
    seeds_x[i] = int(x)
    seeds_y[i] = int(y)


pygame.init()
size = width, height = (MATRIX_L, MATRIX_L)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    for i in range(N):
        dots[i].edges()
        dots[i].join(dots)
        dots[i].update()
        seeds_x[i] = int(dots[i].position[0])
        seeds_y[i] = int(dots[i].position[1])

        if seeds_x[i] > MATRIX_L:
            seeds_x[i] = 0
        if seeds_y[i] > MATRIX_L:
            seeds_y[i] = 0

    voronoi(matrix, matrix2, seeds_x, seeds_y, N, threaded)

    for j in range(MATRIX_L):
        for i in range(MATRIX_L):
            c = matrix[i*MATRIX_L + j]*2
            if c > 255: c = 255
            elif c < 0: c = 0
            c = (255 - c)
            # print(c)
            screen.set_at((i, j), (c, 0 , 50))
    
    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())