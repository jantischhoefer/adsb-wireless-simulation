import geopy.distance
import great_circle_calculator.great_circle_calculator as gcc
from numpy import random

import ADSB
import Parameters
import Transmission


class Plane:
    # id: aircraft id, position: lon-lat, height: [m], speed: [m/s], waypoints: lon-lat 
    def __init__(self, id, position=(105.808817, 21.028511), height=1000, speed=250,
                 waypoints=[(106.660172, 10.762622)], callSign="KLM123"):
        self.id = id
        self.ICAO = hex(random.randint(1, 16777214))[2:]  # create random ICAO address up to FFFFFF
        self.callSign = callSign
        if(len(self.callSign) > 8):
            self.callSign = self.callSign[0:8]
        self.position = position
        self.height = height
        self.speed = speed
        self.waypoints = waypoints
        self.adsb_coder = ADSB.ADSB_coder()

    # updates the position after x seconds
    def updatePos(self, timestep):
        if (len(self.waypoints) < 1):
            return self.position  # waypoints empty.
        # always fly towards the first waypoint in the list; when it is reached, delete it
        # determine distance
        dist = geopy.distance.distance(self.position[::-1], self.waypoints[0][::-1]).m  # geopy expects lat-lon order
        # determine fraction of distance that can be covered in timestep.
        frac = self.speed * timestep / dist
        # determine coordinates of new position
        self.position = gcc.intermediate_point(self.position, self.waypoints[0], frac)
        # if waypoint was reached (or overshot), remove
        if (frac > 1.0):
            self.waypoints.remove(self.waypoints[0])

        return self.position

    def transmit(self, groundstations, commSat, data):

        transmission = []

        # Check Range
        for element in groundstations:
            if self.inRange(element):
                x = Transmission.Transmission(data, self.id, False, element.id, SNRdB=Parameters.plane_to_groundstation_SNRdB,
                                              carrier_freq=Parameters.adsb_freq)
                transmission.append(x)

        transmission.append(Transmission.Transmission(data, self.id, False, commSat.id, channel_type='rice',
                                                      SNRdB=Parameters.plane_to_satellite_SNRdB, carrier_freq=Parameters.adsb_freq))

        return transmission

    def transmitPosition(self, groundstations, commSat):
        # always send pairs of positions
        transmission = self.transmit(groundstations, commSat,
                                     self.adsb_coder.encodePosition(17, 5, self.ICAO, 0, 1, self.height,
                                                                    self.position[1], self.position[0]))
        transmission += self.transmit(groundstations, commSat,
                                      self.adsb_coder.encodePosition(17, 5, self.ICAO, 0, 1, self.height,
                                                                     self.position[1], self.position[0]))
        return transmission

    def transmitIdentification(self, groundstations, commSat):
        return self.transmit(groundstations, commSat,
                             self.adsb_coder.encodeIdentification(17, 5, self.ICAO, 2, self.callSign, 4))

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
