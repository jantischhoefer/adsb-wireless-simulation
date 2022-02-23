import ADSB
import Parameters


class Groundstation:
    def __init__(self, id, position, name):
        self.id = id
        self.name = name
        self.adsb_coder = ADSB.ADSB_coder()
        self.position = position
        self.recRange = Parameters.ground_range
        self.receivedPositions = []
        self.numReceivedMessagesFromPlane = 0
        self.numReceivedMessagesFromSat = 0
        self.numCorruptedMessagesFromPlane = 0
        self.numCorruptedMessagesFromSat = 0

    def receive(self, transmission):

        for element in transmission:
            if element.dest == self.id:
                transmittedData = element.transmit()
                if(element.src_is_satellite == True):
                    self.numReceivedMessagesFromSat += 1
                else:
                    self.numReceivedMessagesFromPlane += 1

                # Process multiple positions received
                # to decode msg, use msg = self.adsb_coder.decode(recData[i])
                # to identify message type, use isinstance(msg, ADSB.ADSB_identification_msg) or isinstance(msg, ADSB.ADSB_positional_msg)
                # to get coordinates from positional message, use msg.decodedLat and msg.decodedLon ONLY if msg.latLonDecoded == True
                msg = self.adsb_coder.decode(transmittedData, True)
                if (isinstance(msg, ADSB.ADSB_positional_msg)):
                    # print(self.name, "received")
                    if (msg.latLonDecoded == True):
                        self.receivedPositions.append((msg.decodedLon, msg.decodedLat, msg.ICAOaddress))
                elif (isinstance(msg, bool)):
                    if msg == False:
                        # message checksum failed
                        if (element.src_is_satellite == True):
                            self.numCorruptedMessagesFromSat += 1
                        else:
                            self.numCorruptedMessagesFromPlane += 1

    def printCorruptedMessageRate(self):

        corruptionRate = "%.2f" % (((self.numCorruptedMessagesFromSat+self.numCorruptedMessagesFromPlane) / (self.numReceivedMessagesFromPlane + self.numReceivedMessagesFromSat)) * 100)
        corruptionRateSat = "%.2f" % (((self.numCorruptedMessagesFromSat) / (self.numReceivedMessagesFromSat+0.0001)) * 100)  # prevent div/0
        corruptionRatePlane = "%.2f" % (((self.numCorruptedMessagesFromPlane) / (self.numReceivedMessagesFromPlane+0.0001)) * 100)  # prevent div/0
        print("Groundstation " + self.name + " received " + corruptionRate + "% corrupted messages.")
        print("  Groundstation " + self.name + " received " + corruptionRatePlane + "% corrupted messages from planes. (of " + str(self.numReceivedMessagesFromPlane) + ")")
        print("  Groundstation " + self.name + " received " + corruptionRateSat + "% corrupted messages from satellites. (of " + str(self.numReceivedMessagesFromSat) + ")")