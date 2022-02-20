import matplotlib.pyplot as plt

import CommSat
import Groundstation
import Plane


class Simulation:

    def __init__(self, timeStep):
        self.realFlightpath = []
        self.recFlightpathHanoi = []
        self.recFlightpathSaigon = []
        self.satPath = []
        self.timeStep = timeStep  # Seconds?

    def run(self):
        plane = Plane.Plane("Plane_ID")
        hanoiAirport = Groundstation.Groundstation("Hanoi_ID", (105.808817, 21.028511))
        saigonAirport = Groundstation.Groundstation("Saigon_ID", (106.660172, 10.762622))
        groundstation = [hanoiAirport, saigonAirport]
        commSat = CommSat.CommSat()

        while not plane.atDestination():
            # Clear transmission
            transmission = []

            # Update the position of plane
            currentPos = plane.updatePos(self.timeStep)
            self.realFlightpath.append(currentPos)

            # Transmission
            transmission = plane.transmit(groundstation, commSat)  # Transmission[data, transmitTo, from]

            commSat.receive(transmission)  # data.mod, data.noise, data.demod ... -> commSat.data

            for element in groundstation:
                transmission.append(commSat.transmit(element))  # Transmission[commSat.data, groundstation, from]

            # Save received position
            self.recFlightpathHanoi.append(groundstation[0].receive(transmission))  # data.mod, data.noise, data.demod ... -> return pos
            self.recFlightpathSaigon.append(groundstation[1].receive(transmission))

    def plot(self):
        img = plt.imread("img/map.jpg")
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[99.4, 116.5, 9.4, 23.2])
        # Add Comm Sat to plot
        ax.scatter(x=110, y=18, c='r', marker='x', label='Communication Satellite')
        # Add range of groundstation
        rangeHanoi = plt.Circle((105.808817, 21.028511), 3.4, color='g', alpha=0.3)
        rangeSaigon = plt.Circle((106.660172, 10.762622), 3.4, color='g', alpha=0.3)
        ax.add_patch(rangeHanoi)
        ax.add_patch(rangeSaigon)
        # Add real flight path to plot
        ax.scatter(*zip(*self.realFlightpath), s=1.0, label='Real Flightpath')
        # Add received flight path to plot
        ax.scatter(*zip(*self.recFlightpathHanoi), s=1.0, marker=',', c='r', label='Received Flightpath Hanoi')
        ax.scatter(*zip(*self.recFlightpathSaigon), s=1.0, marker=',', c='yellow', label='Received Flightpath Saigon')
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
