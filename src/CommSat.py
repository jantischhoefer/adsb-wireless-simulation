import Transmission


class CommSat:
    # pos: lon-lat, height: [m] 400km orbit, speed: [m/s] ~27.000km/hm waypoints: lon-lat, default=97200000
    def __init__(self):
        # self.id = 'sat-' + str(uuid.uuid1())
        self.id = "Sat_ID"
        self.data = []

    def transmit(self, groundstations):

        transmission = []
        for element in self.data:
            for gs in groundstations:
                transmission.append(Transmission.Transmission(element.data, self.id, gs.id, None, None))
            self.data.remove(element)

        #print("ComSat transmit:", transmission)

        return transmission

    def receive(self, transmission):

        for element in transmission:
            if element.dest == self.id:
                #print("ComSat received data")

                # Perform wireless shit!!!!!!!!!

                self.data.append(element)
