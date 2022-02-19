import geopy.distance
import great_circle_calculator.great_circle_calculator as gcc

import Transmission


class Plane:

    def __init__(self):
        self.identification = None
        self.position = (105.804817, 21.028511)  # lon-lat, Hanoi
        self.height = 0
        self.speed = 1800  # m/s
        self.waypoints = [(106.660172, 10.762622)]  # lon-lat, Saigon

    # updates the position after x seconds
    def updatePos(self, timestep):
        if (len(self.waypoints) < 1):
            return  # waypoints empty.
        # always fly towards the first waypoint in the list; when it is reached, delete it
        # determine distance
        dist = geopy.distance.distance(self.position[::-1], self.waypoints[0][::-1]).m  # geopy expects lat-lon order
        # determine fraction of distance that can be covered in timestep.
        frac = self.speed * timestep / dist
        # determine coordinates of new position
        self.position = gcc.intermediate_point(self.position, self.waypoints[0], frac)
        # if waypoint was reached (or overshot), remove
        if (frac > 1.0):
            self.waypoints.pop()

        return self.position

    def transmit(self, groundstation, commSat):

        transmission = []

        data = self.encodeADSBhex()

        # Check Range
        if self.inRange(groundstation):
            transmission.append(Transmission.Transmission(data, self.identification, groundstation.identification))

        if self.inRange(commSat):
            transmission.append(Transmission.Transmission(data, self.identification, commSat.identification))

        return transmission

    def atDestination(self):
        if len(self.waypoints) < 1:
            return True
        else:
            return False

    def inRange(self, destination):
        dist = geopy.distance.distance(self.position[::-1], destination.position[::-1]).m
        if dist > destination.recRange:
            return False
        else:
            return True

    def encodeADSBhex(self):
        return self.position
