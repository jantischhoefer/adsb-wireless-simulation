import geopy.distance
import great_circle_calculator.great_circle_calculator as gcc

class CommSat:
    position = (0,0) # lon-lat
    height = 400000 # 400km orbit
    speed = 97200000 # m/s ~27.000km/h
    waypoints = [] # lon-lat

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