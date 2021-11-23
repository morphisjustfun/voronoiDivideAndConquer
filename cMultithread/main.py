from ctypes import *
import numpy as np
from numpy.ctypeslib import ndpointer 
import struct
import math
import pygame as pg
import sys
from perlin_noise import PerlinNoise
from random import randint
import time

#Pygame initialization
pg.init()
size = 9
seeds = 100
wSize = width, height = 2**size, 2**size
screen = pg.display.set_mode(wSize)
black = 0, 0, 0
white = 255, 255, 255

#Ctypes initialization
_doublepp = ndpointer(dtype=np.uintp, ndim=1, flags='C')
_dll  = CDLL("cMultithread/bridge.so")

_getMatrix = _dll.getMatrix 
_getMatrix.argtypes = [_doublepp, c_int, c_int, ndpointer(c_double, flags="C_CONTIGUOUS"), ndpointer(c_double, flags="C_CONTIGUOUS"), c_int]
_getMatrix.restype = None 

matrix = np.arange((2**(size+size))).reshape((2**(size), 2**(size)))
matrixPtr = (matrix.__array_interface__['data'][0]  + np.arange(matrix.shape[0])*matrix.strides[0]).astype(np.uintp)

randomSeedsX = np.random.randint(2**size, size=seeds)
randomSeedsY = np.random.randint(2**size, size=seeds)

seedsX = np.array(randomSeedsX, dtype=np.float64)
seedsY = np.array(randomSeedsY, dtype=np.float64)

_getMatrix(matrixPtr, size, seeds, seedsX, seedsY, 6)

# densityBASE =  "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# maxDistance = math.sqrt(2)*(2**size)
# density = ""
# for i in range(len(densityBASE)):
#     for j in range(int(maxDistance)//len(densityBASE)):
#         density += densityBASE[i]

# for j in range(len(matrix)):
#     s = ""
#     for i in range(len(matrix[j])):
#         s += density[int(struct.unpack("d", struct.pack("q", int(bin((matrix[j][i])), 2)))[0])%len(density)]*2
#     print (s)

# for j in range(len(matrix)):
#     for i in range(len(matrix[j])):
#         c = (struct.unpack("d", struct.pack("q", int(bin((matrix[j][i])), 2)))[0]+1)
#         screen.set_at((j, i), (c, c, c))

randomSeedsX = np.random.randint(2**size, size=seeds)
randomSeedsY = np.random.randint(2**size, size=seeds)

noise = PerlinNoise(octaves=10, seed=1)

ss = 0

while 1:
    
    for event in pg.event.get():
        if event.type == pg.QUIT: sys.exit()

    screen.fill(black)

    for i in range(len(randomSeedsX)):
        randomSeedsX[i] = randomSeedsX[i] + randint(-5, 5)
        randomSeedsY[i] = randomSeedsY[i] + randint(-5, 5)

    seedsX = np.array(randomSeedsX, dtype=np.float64)
    seedsY = np.array(randomSeedsY, dtype=np.float64)

    _getMatrix(matrixPtr, size, seeds, seedsX, seedsY, 1)
    time.sleep(5)
    
    for j in range(len(matrix)):
        for i in range(len(matrix[j])):
            c = (struct.unpack("d", struct.pack("q", int(bin((matrix[j][i])), 2)))[0]+1)
            screen.set_at((j, i), (c, c, c))
    
    pg.image.save(screen, "ss/" + str(ss)+".jpg")

    ss+=1
    
    pg.display.flip()