import Transmission


class CommSat:
    # pos: lon-lat, height: [m] 400km orbit, speed: [m/s] ~27.000km/hm waypoints: lon-lat, default=97200000
    def __init__(self):
        # self.id = 'sat-' + str(uuid.uuid1())
        self.id = "Sat_ID"
        self.data = None

    def transmit(self, groundstation):

        transmission = Transmission.Transmission(self.data, self.id, groundstation.id, None, None)

        print("ComSat transmit:", transmission)

        return transmission

    def receive(self, transmission):

        for element in transmission:
            if element.dest == self.id:
                originalData = element.data
                print("ComSat received data")

                # Perform wireless shit!!!!!!!!!

                recData = originalData
                self.data = recData
