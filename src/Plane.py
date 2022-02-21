import geopy.distance
import great_circle_calculator.great_circle_calculator as gcc

import Transmission


class Plane:
    # id: aircraft id, position: lon-lat, height: [m], speed: [m/s], waypoints: lon-lat 
    def __init__(self, id, position=(105.808817, 21.028511), height=0, speed=1800, waypoints=[(106.660172, 10.762622)]):
        self.id = id
        self.position = position
        self.height = height
        self.speed = speed
        self.waypoints = waypoints

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

        # TODO David
        # data = self.encodeADSBhex()
        data = self.position

        # Check Range
        for element in groundstation:
            if self.inRange(element):
                x = Transmission.Transmission(data, self.id, element.id, None, None)
                print("Plane transmit:", x, element.id)
                transmission.append(x)

        transmission.append(Transmission.Transmission(data, self.id, commSat.id, None, None))

        return transmission

    def atDestination(self):
        if len(self.waypoints) < 1:
            return True
        else:
            return False

    def inRange(self, destination):
        dist = geopy.distance.distance(self.position[::-1], destination.position[::-1]).m
        if dist > destination.recRange:
            print("NO", destination.id)
            return False
        else:
            print("YES", destination.id)
            return True

    def encodeADSBhex(self):
        return self.position
