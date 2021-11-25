from DelaunayTriangulation import *
import time
import random

def generateRandomPoints(n, w, h):
  points = set()
  while len(points) < n:
    points.add((random.randint(0, w),random.randint(0, h)))
  return list(points)

def testVoronoiByDelaunayTriangulation(points):
  t = time.time()
  triangles = getDelaunayTriangulationByBowyerWatson(points) # O(n^2)
  v = getVoronoiDiagramFromDelaunayTriangulation(triangles, 100) # O(n)
  return time.time() - t

'''
print(
  testVoronoiByDelaunayTriangulation(
    generateRandomPoints(100, 1023, 1023)
  )
)
'''
