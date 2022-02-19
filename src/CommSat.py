import geopy.distance
import great_circle_calculator.great_circle_calculator as gcc

import Transmission


class CommSat:

    def __init__(self):
        self.identification = None
        self.data = None
        self.received = False
        self.position = (0, 0)  # lon-lat
        self.height = 400000  # 400km orbit
        self.speed = 97200000  # m/s ~27.000km/h
        self.waypoints = []  # lon-lat
        self.recRange = 0

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

    def transmit(self, groundstation):

        transmission = []

        # Check Range
        if self.inRange(groundstation) and self.received:
            transmission.append(Transmission.Transmission(self.data, self.identification, groundstation.identification))
            self.received = False

        return transmission

    def receive(self, transmission):

        for element in transmission:
            if element.dest == self.identification:
                originalData = element.data

                # Perform wireless shit!!!!!!!!!

                recData = originalData
                self.data = recData
                self.received = True

    def inRange(self, destination):
        dist = geopy.distance.distance(self.position[::-1], destination.position[::-1]).m
        if dist > destination.recRange:
            return False
        else:
            return True
