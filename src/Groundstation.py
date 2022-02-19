class Groundstation:

    def __init__(self):
        self.identification = None
        self.position = (0, 0)
        self.recRange = 0

    def receive(self, transmission):
        recData = []
        for element in transmission:
            if element.dest == self.identification:
                originalData = element.data

                # Perform wireless shit!!!!!!!!!

                recData.append(originalData)

        # Process multiple positions received
        planePosition = recData[0]

        return planePosition

