import ADSB

class Groundstation:

    # id should be 'HAN' or 'SGN'
    def __init__(self, id, position, name):
        self.id = id
        self.name = name
        self.adsb_coder = ADSB.ADSB_coder()
        self.position = position
        self.recRange = 370000  # 370km
        self.receivedPositions = []
        self.numReceivedMessages = 0
        self.numCorruptedMessages = 0

    def receive(self, transmission):

        for element in transmission:
            if element.dest == self.id:
                # Perform wireless shit!!!!!!!!!
                transmittedData = element.transmit()
                self.numReceivedMessages += 1

                #print(len(transmittedData))
                # Process multiple positions received
                # to decode msg, use msg = self.adsb_coder.decode(recData[i])
                # to identify message type, use isinstance(msg, ADSB.ADSB_identification_msg) or isinstance(msg, ADSB.ADSB_positional_msg)
                # to get coordinates from positional message, use msg.decodedLat and msg.decodedLon ONLY if msg.latLonDecoded == True
                msg = self.adsb_coder.decode(transmittedData, True)
                if(isinstance(msg, ADSB.ADSB_positional_msg)):
                    #print(self.name, "received")
                    if(msg.latLonDecoded == True):
                        self.receivedPositions.append((msg.decodedLon, msg.decodedLat, msg.ICAOaddress))
                elif(isinstance(msg, bool)):
                    if msg == False:
                        # message checksum failed
                        self.numCorruptedMessages += 1

    def getCorruptedMessageRate(self):
        return (self.numCorruptedMessages / self.numReceivedMessages)