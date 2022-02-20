import utils

# can encode, decode and print the message part of an ADSB position transmission
class ADSB_positional_msg:
    surveillanceStatus = 0
    singleAntennaFlag = 0
    altitude = 0
    time = 0
    cprFormat = 0
    latitude = 0
    longitude = 0

    def decodeMessage(self):
        return self

    def encodeMessage(self, surveillanceStatus, singleAntennaFlag, altitude, time, cprFormat, latitude, longitude):
        return ""

    def printContents(self):
        dataStr = ""
        dataStr += "surveillanceStatus: " + str(self.surveillanceStatus) + "\n"
        dataStr += "singleAntennaFlag: " + str(self.singleAntennaFlag) + "\n"
        dataStr += "altitude: " + str(self.altitude) + "\n"
        dataStr += "time: " + str(self.time) + "\n"
        dataStr += "cprFormat: " + str(self.cprFormat) + "\n"
        dataStr += "latitude: " + str(self.latitude) + "\n"
        dataStr += "longitude: " + str(self.longitude) + "\n"
        print(dataStr)


# can encode, decode and print the message part of an ADSB identification transmission
class ADSB_identification_msg:
    ICAO = ""
    vortexCategory = 0
    callSign = ""
    typeCode = 4

    def decodeMessage(self):
        return self

    def encodeMessage(self, vortexCategory, callSign):
        # type code
        typeCodeBits = bin(self.typeCode)[2:]
        while len(typeCodeBits) < 5:
            typeCodeBits = "0" + typeCodeBits

        # vortex category
        vortexCategoryBits = bin(vortexCategory)[2:]
        while len(vortexCategoryBits) < 3:
            vortexCategoryBits = "0" + vortexCategoryBits

        # callSign (convert every char to int, from there to binary and hex)
        callSignBits=""
        for char in callSign:
            binaryChar = bin(utils.adsb_char_to_int(char))[2:]
            while len(binaryChar) < 6:
                binaryChar = "0" + binaryChar
            callSignBits += binaryChar
        while len(callSignBits) < 48:
            callSignBits = callSignBits + "100000" # add spaces to the end

        return hex(int(typeCodeBits + vortexCategoryBits + callSignBits, 2))

    def printContents(self):
        dataStr = ""
        dataStr += "ICAO: " + str(self.ICAO) + "\n"
        dataStr += "vortexCategory: " + str(self.vortexCategory) + "\n"
        dataStr += "callSign: " + str(self.callSign) + "\n"
        print(dataStr)

class ADSB_coder:

    # when ADSB-coder is used in a plane, transpondercapability and ICAO address can be set hee
    transponderCapability = 6
    ICAOaddress = ""
    callSign = "YOMAMA"
    vortexCategory = 3
    downlinkFormat = 17 # default for civil aircraft

    def initForPlane(self, transponderCapability, ICAOaddress, callSign, vortexCategory, downlinkFormat):
        self.transponderCapability = transponderCapability
        self.ICAOaddress = ICAOaddress
        self.callSign = callSign
        self.vortexCategory = vortexCategory
        self.downlinkFormat = downlinkFormat

    def calculateCRC(self, msg):
        generator = "1111111111111010000001001"
        binMSG=bin(int(msg, 16))[2:]
        # fill up with zeroes
        binMSG = binMSG.ljust(112, '0')

        # calculate the parity using generator and data (CRC)
        for i in range(88):
            if binMSG[i] == '1':
                xor = bin(int(binMSG[i:i+25], 2) ^ int(generator, 2))[2:]
                xor = str(xor).zfill(25)
                # replace part of string
                binMSG = binMSG[0:i] + xor + binMSG[i+25:]
        remainder = binMSG[-24:]
        return hex(int(remainder, 2))[2:].upper().zfill(6).upper()

    def decode(self, msgHex):
        # first, check crc
        if self.calculateCRC(msgHex)
        return ""

    # encode message prefix containing downlink format and transponder capability
    def encodeADSBprefix(self):
        dFcTbin = bin((self.downlinkFormat<<3) | self.transponderCapability)[2:]
        ICAObin = bin(int(self.ICAOaddress, 16))[2:]
        while len(ICAObin) < 24:
            ICAObin = "0" + ICAObin
        return hex(int(dFcTbin + ICAObin, 2)).upper()

    def encodePosition(self, surveillanceStatus, singleAntennaFlag, altitude, time, cprFormat, latitude, longitude):
        ADSB_positional_msg.encodeMessage(surveillanceStatus, singleAntennaFlag, altitude, time, cprFormat, latitude, longitude)

    def encodeIdentification(self):
        prefix = self.encodeADSBprefix()[2:]
        identMSG = ADSB_identification_msg()
        msgPart = identMSG.encodeMessage(self.vortexCategory, self.callSign)[2:]
        crc = self.calculateCRC(prefix + msgPart)
        return (prefix + msgPart + crc).upper()
