class Groundstation:

    # id should be 'HAN' or 'SGN'
    def __init__(self, id, position):
        self.id = id
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
        if len(recData) > 0:
            planePosition = recData[0]
        else:
            planePosition = (0,0)

        print("Groundstation received:", planePosition)

        return planePosition
