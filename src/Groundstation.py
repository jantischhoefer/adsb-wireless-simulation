import ADSB

class Groundstation:

    # id should be 'HAN' or 'SGN'
    def __init__(self, id):
        self.id = id
        self.position = (0, 0)
        self.recRange = 0
        self.adsb_coder = ADSB.ADSB_coder()

    def receive(self, transmission):
        recData = []
        for element in transmission:
            if element.dest == self.id:
                originalData = element.data

                # Perform wireless shit!!!!!!!!!

                recData.append(originalData)

        # Process multiple positions received
        # to decode msg, use msg = self.adsb_coder.decode(recData[i])
        # to identify message type, use isinstance(msg, ADSB.ADSB_identification_msg) or isinstance(msg, ADSB.ADSB_positional_msg)
        # to get coordinates from positional message, use msg.decodedLat and msg.decodedLon

        planePosition = recData[0]

        return planePosition
