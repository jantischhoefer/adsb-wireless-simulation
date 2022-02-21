import matplotlib.pyplot as plt

import CommSat
import Groundstation
import Plane


class Simulation:

    def __init__(self, timeStep):
        self.realFlightpath = []
        self.recFlightpath = []
        self.satPath = []
        self.timeStep = timeStep  # Seconds?

    def run(self):
        plane = Plane.Plane("Plane_ID")
        groundstation = Groundstation.Groundstation("Groundstation_ID")
        commSat = CommSat.CommSat()

        while not plane.atDestination():
            # Update the position of plane
            currentPos = plane.updatePos(self.timeStep)
            self.realFlightpath.append(currentPos)

            # Update the position of sat
            satPos = commSat.updatePos(self.timeStep)
            self.satPath.append(satPos)

            # Transmission
            transmission = [plane.transmitPosition(groundstation, commSat)]  # Transmission[data, transmitTo, from]

            commSat.receive(transmission)  # data.mod, data.noise, data.demod ... -> commSat.data
            transmission.append(commSat.transmit(groundstation))  # Transmission[commSat.data, groundstation, from]

            recPos = groundstation.receive(transmission)  # data.mod, data.noise, data.demod ... -> return pos

            # Save received position
            self.recFlightpath.append(recPos)

    def plot(self):
        plt.scatter(*zip(*self.realFlightpath))
        plt.show()


if __name__ == "__main__":
    simulation = Simulation(1)  # 1 second
    simulation.run()
    simulation.plot()
