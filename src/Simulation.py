import matplotlib.pyplot as plt
from collections import Counter

import CommSat
import Groundstation
import Plane


class Simulation:

    def __init__(self, timeStep):
        self.realFlightpaths = []
        self.satPath = []
        self.timeStep = timeStep  # Seconds?
        self.groundstations = []
        self.planes = []

    def run(self):

        hanoiAirport = Groundstation.Groundstation("Hanoi_ID", (105.808817, 21.028511), "Hanoi")
        saigonAirport = Groundstation.Groundstation("Saigon_ID", (106.660172, 10.762622), "HCMC")
        self.groundstations = [hanoiAirport, saigonAirport]

        plane1 = Plane.Plane("Plane_ID")
        plane2 = Plane.Plane("Plane_ID_2", waypoints=[(108.660172, 17.762622), (106.660172, 10.762622)])
        self.planes = [plane1, plane2]
        commSat = CommSat.CommSat()

        allPlanesArrived = False

        while not allPlanesArrived:
            # Clear transmission
            transmission = []

            # Update the position of planes
            allPlanesArrived = True
            for plane in self.planes:
                newPos = plane.updatePos(self.timeStep)
                self.realFlightpaths.append((newPos[0], newPos[1], plane.ICAO))
                # Transmission
                transmission += plane.transmitPosition(self.groundstations, commSat)  # Transmission[data, transmitTo, from]
                transmission += plane.transmitIdentification(self.groundstations, commSat)
                # check if all planes arrived
                if not plane.atDestination():
                    allPlanesArrived = False

            commSat.receive(transmission)  # data.mod, data.noise, data.demod ... -> commSat.data

            #Satellite transmits to all groundstations
            transmission += commSat.transmit(self.groundstations)  # Transmission[commSat.data, groundstations, from]

            # Save received position
            for gs in self.groundstations:
                gs.receive(transmission) # data.mod, data.noise, data.demod ... -> return pos

    def plot(self):
        img = plt.imread("img/map.JPG")
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[99.4, 116.5, 9.4, 23.2])
        # Add Comm Sat to plot
        ax.scatter(x=110, y=18, c='r', marker='x', label='Communication Satellite')
        # Add range of groundstation
        rangeHanoi = plt.Circle((105.808817, 21.028511), 3.4, color='g', alpha=0.3)
        rangeSaigon = plt.Circle((106.660172, 10.762622), 3.4, color='g', alpha=0.3)
        ax.add_patch(rangeHanoi)
        ax.add_patch(rangeSaigon)
        # Add real flight paths to plot
        lons, lats, icaos = zip(*self.realFlightpaths)
        icaoset = set(icaos)
        for icao in icaoset:
            lonsnew = ()
            latsnew = ()
            for element in self.realFlightpaths:
                if element[2] == icao:
                    lonsnew += (element[0],)
                    latsnew += (element[1],)
            label = "Real Flightpath of " + icao
            ax.scatter(lonsnew, latsnew, s=1.0, c="#"+icao, label=label)
        # Add received flight paths to plot
        # first identify number of planes


        for gs in self.groundstations:
            lons, lats, icaos = zip(*gs.receivedPositions)
            icaoset = set(icaos)
            for icao in icaoset:
                lonsnew = ()
                latsnew = ()
                for element in gs.receivedPositions:
                    if(element[2] == icao):
                        lonsnew += (element[0],)
                        latsnew += (element[1],)
                label = "Received Flightpaths of " + icao + " in " + gs.name
                color = int(icao, 16) + int(gs.name.lower(), 36)
                ax.scatter(lonsnew, latsnew, s=1.0, marker=',', c="#" + hex(color)[2:8], label=label)

        # Add groundstations to plot
        ax.scatter(x=105.808817, y=21.028511, c='g', marker='x', label='Hanoi Airport')
        ax.scatter(x=106.660172, y=10.762622, c='g', marker='x', label='Saigon Airport')

        plt.xlim(99.4, 116.5)
        plt.ylim(9.4, 23.2)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.legend(fontsize=8)

        plt.show()


if __name__ == "__main__":
    simulation = Simulation(1)  # 1 second
    simulation.run()
    simulation.plot()
