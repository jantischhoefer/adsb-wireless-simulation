import matplotlib.pyplot as plt

import CommSat
import Groundstation
import Parameters
import Plane


class Simulation:

    def __init__(self):
        self.realFlightpaths = []
        self.timeStep = Parameters.sim_timestep
        self.groundstations = Parameters.groundstations
        self.planes = Parameters.planes

    def run(self):

        commSat = CommSat.CommSat()

        allPlanesArrived = False

        timePassed = 0.0
        while not allPlanesArrived:
            # Clear transmission
            transmission = []

            # Update the position of planes
            allPlanesArrived = True
            for plane in self.planes:
                if not plane.atDestination():
                    newPos = plane.updatePos(self.timeStep)
                    self.realFlightpaths.append((newPos[0], newPos[1], plane.ICAO))
                    # Transmission
                    transmission += plane.transmitPosition(self.groundstations,
                                                           commSat)  # Transmission[data, transmitTo, from]
                    # identification messages are published at a frequency of 0.2Hz
                    if (timePassed % 5 == 0):
                        transmission += plane.transmitIdentification(self.groundstations, commSat)
                    # not all planes arrived yet
                    allPlanesArrived = False

            # Satellite transmits to all groundstations - this happens with a delay of one timestep
            transmission += commSat.transmit(
                self.groundstations)  # Transmission[commSat.data, groundstations, from]

            commSat.receive(transmission)  # data.mod, data.noise, data.demod ... -> commSat.data


            # Save received position
            for gs in self.groundstations:
                gs.receive(transmission)  # data.mod, data.noise, data.demod ... -> return pos

            timePassed += self.timeStep
        print("Total time passed in Simulation (min): ", timePassed / 60.0)
        for gs in self.groundstations:
            gs.printCorruptedMessageRate()

    def plot(self):
        img = plt.imread("img/map.JPG")
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[99.4, 116.5, 9.4, 23.2])
        # Add Comm Sat to plot
        ax.scatter(x=110, y=18, c='r', marker='x', label='Communication Satellite')
        # Add range of groundstation
        for gs in self.groundstations:
            rangepatch = plt.Circle(gs.position, gs.recRange * 0.0000093, color='g',
                       alpha=0.3)
            ax.add_patch(rangepatch)

        # Add real flight paths to plot
        lons, lats, icaos = zip(*self.realFlightpaths)
        icaoset = set(icaos)
        scatterPlots = []
        for icao in icaoset:
            lonsnew = ()
            latsnew = ()
            for element in self.realFlightpaths:
                if element[2] == icao:
                    lonsnew += (element[0],)
                    latsnew += (element[1],)
            label = "Real Flightpath of " + icao
            color = hex(int(icao, 16))[2:8]
            while(len(color) < 6):
                color = "0" + color
            scatterPlot = ax.scatter(lonsnew, latsnew, s=1.0, c="#" + color, alpha=0.2, label=label)
            scatterPlots.append(scatterPlot)

        # Add received flight paths to plot
        # first identify number of planes
        for gs in self.groundstations:
            lons, lats, icaos = zip(*gs.receivedPositions)
            icaoset = set(icaos)
            for icao in icaoset:
                lonsnew = ()
                latsnew = ()
                for element in gs.receivedPositions:
                    if (element[2] == icao):
                        lonsnew += (element[0],)
                        latsnew += (element[1],)
                label = "Received Flightpaths of " + icao + " in " + gs.name
                color = hex(int(icao, 16) + int(gs.name.lower(), 36))[2:8]
                while(len(color) < 6):
                    color = "0" + color
                scatterPlot = ax.scatter(lonsnew, latsnew, s=1.0, marker=',', c="#" + color, label=label)
                scatterPlots.append(scatterPlot)

        # Add groundstations to plot
        ax.scatter(x=105.808817, y=21.028511, c='g', marker='x', label='Hanoi Airport')
        ax.scatter(x=106.660172, y=10.762622, c='g', marker='x', label='Saigon Airport')

        plt.xlim(99.4, 116.5)
        plt.ylim(9.4, 23.2)
        plt.gca().set_aspect('equal', adjustable='box')
        leg = ax.legend(fontsize=8)

        # Enable legend picking
        for legEntry in leg.legendHandles:
            legEntry.set_picker(5)

        def on_pick(event):
            # On the pick event, find the original line corresponding to the legend
            # proxy line, and toggle its visibility.
            legEntry = event.artist
            for scatterPlot in scatterPlots:
                if scatterPlot.get_label() == legEntry.get_label():
                    visible = not scatterPlot.get_visible()
                    scatterPlot.set_visible(visible)
                    legEntry.set_alpha(1.0 if visible else 0.2)
                    fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', on_pick)

        plt.show()


if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()
    simulation.plot()
