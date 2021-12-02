import random
import math
import numpy as np

size = width, height = (512, 512)

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def randomVector():
    v = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
    return v / np.linalg.norm(v)

        

class Dot:
    def __init__(self, x, y):
        self.position = np.array([x, y])
        self.velocity = randomVector()
        self.velocity *= random.uniform(0.5, 1.5)
        self.aceleration = np.array([0, 0])
        self.maxForce = 1
        self.maxSpeed = 4

    def edges(self):
        if (self.position[0] > width):
            self.position[0] = 0
        elif (self.position[0] < 0):
            self.position[0] = width

        if (self.position[1] > height):
            self.position[1] = 0
        elif (self.position[1] < 0):
            self.position[1] = height

    def align(self, dots):

        perceptionRadius = 20

        steering = np.array([0.0, 0.0])
        totalClose = 0
        for other in dots:
            if other != self:
                d = distance(self.position, other.position)
                if d < perceptionRadius:
                    steering += other.velocity
                    totalClose += 1

        if totalClose > 0:
            steering /= totalClose
            steering = steering * self.maxSpeed /  np.linalg.norm(steering)
            steering -= self.velocity
            if np.linalg.norm(steering) > self.maxForce:
                steering = steering * self.maxForce /  np.linalg.norm(steering)
    
        return steering

    def separation(self, dots):

        perceptionRadius = 30

        steering = np.array([0.0, 0.0])
        totalClose = 0
        for other in dots:
            if other != self:
                d = distance(self.position, other.position)
                if d < perceptionRadius:
                    diff = self.position - other.position
                    diff /= (d*d)
                    steering += diff
                    totalClose += 1

        if totalClose > 0:
            steering /= totalClose
            steering = steering * self.maxSpeed /  np.linalg.norm(steering)
            steering -= self.velocity
            if np.linalg.norm(steering) > self.maxForce:
                steering = steering * self.maxForce /  np.linalg.norm(steering)
    
        return steering

    def cohesion(self, dots):

        perceptionRadius = 40

        steering = np.array([0.0, 0.0])
        totalClose = 0
        for other in dots:
            if other != self:
                d = distance(self.position, other.position)
                if d < perceptionRadius:
                    steering += other.position
                    totalClose += 1

        if totalClose > 0:
            steering /= totalClose
            steering -= self.position
            steering = steering * self.maxSpeed /  np.linalg.norm(steering)
            steering -= self.velocity
            if np.linalg.norm(steering) > self.maxForce:
                steering = steering * self.maxForce /  np.linalg.norm(steering)
    
        return steering
    
    def join(self, dots):
        aligment = self.align(dots)
        cohesion = self.cohesion(dots)
        separation = self.separation(dots)*2
        self.aceleration = separation + aligment + cohesion
    def update(self):
        self.position += self.velocity
        self.velocity += self.aceleration
        self.velocity = self.velocity * self.maxSpeed /  np.linalg.norm(self.velocity)
        