import geopy.distance
import great_circle_calculator.great_circle_calculator as gcc

class Plane:
    # id: aircraft id, position: lon-lat, height: [m], speed: [m/s], waypoints: lon-lat 
    def __init__(self, id, position = (0,0), height = 0, speed = 1800, waypoints = []):
        self.id = id
        self.position = position
        self.height = height
        self.speed = speed
        self.waypoints = waypoints
    

    # updates the position after x seconds
    def updatePos(self, timestep):
        if(len(self.waypoints) < 1):
            return # waypoints empty.
        # always fly towards the first waypoint in the list; when it is reached, delete it
        # determine distance
        dist = geopy.distance.distance(self.position[::-1], self.waypoints[0][::-1]).km # geopy expects lat-lon order
        # determine fraction of distance that can be covered in timestep.
        frac = self.speed * timestep / dist
        # determine coordinates of new position
        self.position = gcc.intermediate_point(self.position, self.waypoints[0], frac)
        # if waypoint was reached (or overshot), remove
        if (frac > 1.0):
            self.waypoints.pop()