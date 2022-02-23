import Parameters
import Transmission


class CommSat:
    def __init__(self):
        self.id = "Sat_ID"
        self.data = []

    def transmit(self, groundstations):

        transmission = []
        for element in self.data:
            for gs in groundstations:
                transmission.append(Transmission.Transmission(element, self.id, True, gs.id, carrier_frequency=Parameters.sat_freq,
                                                              SNRdB=Parameters.sat_SNRdB))
            self.data.remove(element)

        return transmission

    def receive(self, transmission):

        for element in transmission:
            if element.dest == self.id:
                transmitted = element.transmit()

                self.data.append(transmitted)
