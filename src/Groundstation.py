import ADSB

class Groundstation:

    # id should be 'HAN' or 'SGN'
    def __init__(self, id, position):
        self.id = id
        self.adsb_coder = ADSB.ADSB_coder()
        self.position = position
        self.recRange = 370000  # 370km

    def receive(self, transmission):
        recData = []
        for element in transmission:
            if element.dest == self.id:
                originalData = element.data

                # Perform wireless shit!!!!!!!!!

                # TODO David
                # data = self.decodeADSBhex()

                recData.append(originalData)

        # Process multiple positions received
        # to decode msg, use msg = self.adsb_coder.decode(recData[i])
        # to identify message type, use isinstance(msg, ADSB.ADSB_identification_msg) or isinstance(msg, ADSB.ADSB_positional_msg)
        # to get coordinates from positional message, use msg.decodedLat and msg.decodedLon ONLY if msg.latLonDecoded == True

        if len(recData) > 0:
            planePosition = recData[0]
        else:
            planePosition = (0,0)

        print("Groundstation received:", planePosition)

        return planePosition
