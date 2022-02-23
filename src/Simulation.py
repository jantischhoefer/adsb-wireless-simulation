import matplotlib.pyplot as plt

import CommSat
import Groundstation
import Parameters
import Plane


class Simulation:

    def __init__(self, timeStep):
        self.realFlightpaths = []
        self.satPath = []
        self.timeStep = timeStep
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
                    if (timePassed % 5 == 0):
                        transmission += plane.transmitIdentification(self.groundstations, commSat)
                    # not all planes arrived yet
                    allPlanesArrived = False

            commSat.receive(transmission)  # data.mod, data.noise, data.demod ... -> commSat.data

            # Satellite transmits to all groundstations
            transmission += commSat.transmit(self.groundstations)  # Transmission[commSat.data, groundstations, from]

            # Save received position
            for gs in self.groundstations:
                gs.receive(transmission)  # data.mod, data.noise, data.demod ... -> return pos

            timePassed += self.timeStep
        print("Total time passed (min): ", timePassed / 60.0)
        for gs in self.groundstations:
            corruptionRate = "%.2f" % (gs.getCorruptedMessageRate() * 100)
            print("Groundstation " + gs.name + " received " + corruptionRate + "% corrupted messages.")

    def plot(self):
        img = plt.imread("img/map.JPG")
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[99.4, 116.5, 9.4, 23.2])
        # Add Comm Sat to plot
        ax.scatter(x=110, y=18, c='r', marker='x', label='Communication Satellite')
        # Add range of groundstation
        rangeHanoi = plt.Circle((105.808817, 21.028511), Parameters.ground_range * 0.00918, color='g', alpha=0.3)
        rangeSaigon = plt.Circle((106.660172, 10.762622), Parameters.ground_range * 0.00918, color='g', alpha=0.3)
        ax.add_patch(rangeHanoi)
        ax.add_patch(rangeSaigon)
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
            #scatterPlot = ax.scatter(lonsnew, latsnew, s=1.0, c="#" + icao, alpha=0.2, label=label)
            #scatterPlots.append(scatterPlot)
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
                color = int(icao, 16) + int(gs.name.lower(), 36)
                scatterPlot = ax.scatter(lonsnew, latsnew, s=1.0, marker=',', c="#" + hex(color)[2:8], label=label)
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
    simulation = Simulation(Parameters.sim_timestep)  # 5 seconds
    simulation.run()
    simulation.plot()
