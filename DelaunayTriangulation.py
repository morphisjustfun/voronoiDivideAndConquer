from math import dist, pi, acos
from collections import defaultdict


def circumcenter(triangle):
        ax = triangle[0][0]
        ay = triangle[0][1]
        bx = triangle[1][0]
        by = triangle[1][1]
        cx = triangle[2][0]
        cy = triangle[2][1]
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return (ux, uy)

def circumcircle(triangle):
        c = circumcenter(triangle)
        return c, dist(c, triangle[0])

def less_point(p1, p2):
        return (p1[0] < p2[0]) or (p1[0] == p2[0] and p1[1] < p2[1])

def make_edge(p1, p2):
        return (p1, p2) if less_point(p1, p2) else (p2, p1)

def getDelaunayTriangulationByBowyerWatson(points):
        triangulation = set()

        xmin = min(points, key = lambda x: x[0])[0]
        xmax = max(points, key = lambda x: x[0])[0]
        ymin = min(points, key = lambda x: x[1])[1]
        ymax = max(points, key = lambda x: x[1])[1]
        w = abs(xmax-xmin)
        h = abs(ymax-ymin)
        supertriangle = ((xmin - 2*w, ymin - h/2), (xmax + 2*w, ymin - h/2), (xmin + w/2, ymax + h))
        triangulation.add(supertriangle)

        for point in points: # O(n)
                badTriangles = set()
                badEdges = {}
                for triangle in triangulation: # O(n)
                        c, r = circumcircle(triangle)
                        if dist(point, c) < r:
                                for i in range(0, 3):
                                        edge = make_edge(triangle[i], triangle[(i+1)%3])
                                        if edge in badEdges:
                                                badEdges[edge] = True
                                        else:
                                                badEdges[edge] = False
                                badTriangles.add(triangle)
                                
                polygon = []
                for edge in badEdges: # O(n)
                        if badEdges[edge] == False:
                                polygon.append(edge)
                for triangle in badTriangles: # O(n)
                        triangulation.remove(triangle)
                for edge in polygon: # O(n)
                        triangulation.add((edge[0], edge[1], point))
        
        badTriangles = set()
        for triangle in triangulation: # O(n)
                for vertex in triangle:
                        if vertex in supertriangle:
                             badTriangles.add(triangle)
        for triangle in badTriangles: # O(n)
                triangulation.remove(triangle)
        
        return triangulation # TOTAL: O(n^2)

def midpoint(edge):
        return ((edge[0][0]+edge[1][0])/2, (edge[0][1]+edge[1][1])/2)

def ptInTriangle(p, p0, p1, p2):
        dX = p[0]-p2[0]
        dY = p[1]-p2[1]
        dX21 = p2[0]-p1[0]
        dY12 = p1[1]-p2[1]
        D = dY12*(p0[0]-p2[0]) + dX21*(p0[1]-p2[1])
        s = dY12*dX + dX21*dY
        t = (p2[1]-p0[1])*dX + (p0[0]-p2[0])*dY
        if (D<0):
                return s<=0 and t<=0 and s+t>=D
        return s>=0 and t>=0 and s+t<=D

def move_towards(from_, to_, n):
        return (n*(to_[0]-from_[0]) + from_[0], n*(to_[1]-from_[1]) + from_[1])

def dot(vA, vB):
    return vA[0]*vB[0]+vA[1]*vB[1]
def angle(lineA, lineB):
    vA = [(lineA[0][0]-lineA[1][0]), (lineA[0][1]-lineA[1][1])]
    vB = [(lineB[0][0]-lineB[1][0]), (lineB[0][1]-lineB[1][1])]
    dot_prod = dot(vA, vB)
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    return acos(dot_prod/magB/magA)

def getVoronoiDiagramFromDelaunayTriangulation(triangulation, ray_constant):
        edges_circumcenters = {}

        for triangle in triangulation: # O(n)
                c = circumcenter(triangle)
                inside = ptInTriangle(c, *triangle)
                for i in range(0, 3):
                        edge = make_edge(triangle[i], triangle[(i+1)%3])
                        if edge in edges_circumcenters:
                                edges_circumcenters[edge][1] = (c, inside)
                        else:
                                edges_circumcenters[edge] = [(c, inside), None]
        
        voronoi = []
        circumcenters_connections = defaultdict(list)
        for edge, circumcenters in edges_circumcenters.items(): # O(n)
                c1 = circumcenters[0]
                c2 = circumcenters[1]
                if c2 == None:
                        circumcenters_connections[c1].append((midpoint(edge), True)) 
                else:
                        voronoi.append((c1[0], c2[0]))
                        circumcenters_connections[c1].append((c2[0], False))
                        circumcenters_connections[c2].append((c1[0], False))
        
        for c, connections in circumcenters_connections.items(): # O(n)
                if c[1]:
                        for i in range(0, 3):
                                if connections[i][1]:
                                        voronoi.append((c[0], move_towards(c[0], connections[i][0], ray_constant)))
                else:
                        for i in range(0, 3):
                                if connections[i][1]:
                                        lineA = (c[0], connections[i][0])
                                        lineB = (c[0], connections[(i+1)%3][0])
                                        lineC = (c[0], connections[(3+i-1)%3][0])
                                        a1 = angle(lineA, lineB)
                                        a2 = angle(lineA, lineC)
                                        if (a1 + a2) < pi:
                                                voronoi.append((c[0], move_towards(connections[i][0], c[0], ray_constant)))
                                        else:
                                                voronoi.append((c[0], move_towards(c[0], connections[i][0], ray_constant)))
        return voronoi # TOTAL: O(n)