from ctypes import *
import os

#=========================================================
# MARIO SAMA en el código hay 3 partes ke tienes ke editar/hacer.
# Préstale más atención a (FIRST, SECOND, THIRD)
#=========================================================



#=========================================================
# FIRST compile "voronoi.c" with: 
#     gcc -shared -o voronoi_2048.so -fPIC voronoi_2048.c
#=========================================================



#=========================================================
#GLOBALS
#=========================================================

#Global DLL
CVoronoi  = CDLL(os.path.abspath("voronoi_2048.so"))
voronoi = CVoronoi.voronoi_2048
voronoi.argtypes = [POINTER(c_uint16), POINTER(c_int), POINTER(c_int), c_int, c_int]

#Global Constants
MATRIX_L = 2048 #Don't change 2048
MAX_SEEDS = 2000 #Realistic max (to avoid realloc)

#Global Variables
#   you shouldn't define this inside a function (to avoid realloc)
matrix = (c_uint16*(MATRIX_L*MATRIX_L))()
seeds_x = (c_int*MAX_SEEDS)()
seeds_y = (c_int*MAX_SEEDS)()
n_seeds = 0 #This will be setted with set_seeds, dont change it manually
threaded = 1 # 1 yes, 0 no, you choose

#Global Function
#This will preprocess the coords, just in case
def set_seeds(X, Y): # X and Y are arrays
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





#=========================================================
#SECOND define the seeds, no preprocessing needed
# BUT notice that LAT and LON are in separated arrays
#=========================================================

LAT = [100, 512, 3217, 2020, 1889]
LON = [3999, 2003, 1008, 57, 1818]





#=========================================================
#Function calls
#  you can put the above calls where you prefer
#   inside a function or not, not important
#=========================================================

set_seeds(LAT, LON)

voronoi(matrix, seeds_x, seeds_y, n_seeds, threaded)





#=========================================================
#THIRD display the matrix
#=========================================================

#colors = [... n_seeds]
#PAINT LIKE THIS: colors[matrix[i*MATRIX_L + j]]

# ------> GRAPHICAL INTERFACE CODE HERE <-------







