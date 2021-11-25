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
seeds = 50
wSize = width, height = 2**size, 2**size
screen = pg.display.set_mode(wSize)
black = 0, 0, 0
white = 255, 255, 255

#Ctypes initialization
_dll  = CDLL("cMultithread/bridge.so")



_doublepp = ndpointer(dtype=np.uintp, ndim=1, flags='C')

_getMatrix = _dll.getMatrix 
_getMatrix.argtypes = [_doublepp, c_int, c_int, ndpointer(c_double, flags="C_CONTIGUOUS"), ndpointer(c_double, flags="C_CONTIGUOUS"), c_int]
_getMatrix.restype = None 

matrix = np.arange((2**(size+size))).reshape((2**(size), 2**(size)))

matrixPtr = (matrix.__array_interface__['data'][0]  + np.arange(matrix.shape[0])*matrix.strides[0]).astype(np.uintp)

randomSeedsX = np.random.randint(2**size, size=seeds)
randomSeedsY = np.random.randint(2**size, size=seeds)

seedsX = np.array(randomSeedsX, dtype=np.float64)
seedsY = np.array(randomSeedsY, dtype=np.float64)

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
    time.sleep(2)

    for j in range(len(matrix)):
        for i in range(len(matrix[j])):
            c = (struct.unpack("d", struct.pack("q", int(bin((matrix[j][i])), 2)))[0]+1)
            if c < 1: c = 1
            elif c > 255: c = 255
            
            screen.set_at((i, j), (c, c, c))
    
    pg.image.save(screen, "ss/" + str(ss)+".jpg")
    print(ss)
    ss+=1
    
    pg.display.flip()