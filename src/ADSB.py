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
    typeCode=20

    def decodeMessage(self, msg):
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
    vortexCategory = 0
    callSign = ""
    typeCode = 4

    def decodeMessage(self, msg):
        msgBin = bin(int(msg, 16))
        self.typeCode = int(msgBin[0:5], 2)
        self.vortexCategory = int(msgBin[5:8], 2)

        # callSign
        for i in range(8):
            self.callSign += utils.adsb_int_to_char(int(msgBin[8 + i*6:8+i*6+6], 2))

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
        dataStr += "vortexCategory: " + str(self.vortexCategory) + "\n"
        dataStr += "callSign: " + str(self.callSign) + "\n"
        print(dataStr)

class ADSB_coder:

    # when ADSB-coder is used in a plane, transpondercapability and ICAO address can be set hee
    transponderCapability = 5
    ICAOaddress = ""
    callSign = ""
    vortexCategory = 0
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
        if self.calculateCRC(msgHex[:-6]) != msgHex[-6:]:
            print("Checksum of received ADS-B message does not check out. Aborting")
            return

        msgBin = bin(int(msgHex, 16))[2:]
        downlinkFormat = int(msgBin[0:5], 2)
        transponderCapability = int(msgBin[5:8], 2)
        ICAOaddress = hex(int(msgBin[8:32],2))[2:].upper()
        typeCode = int(msgBin[32:37], 2)
        if typeCode >= 1 and typeCode <=4:
            # identification message
            temp = ADSB_identification_msg()
            temp.decodeMessage(msgHex[8:22])
            outStr = "Identification-message received.\n"
            outStr += "DL-Format: " + str(downlinkFormat) + "\n"
            outStr += "Transponder Capability: " + str(transponderCapability) + "\n"
            outStr += "ICAO address: " + str(ICAOaddress) + "\n"
            outStr += "Type Code: " + str(typeCode)
            print(outStr)
            temp.printContents()
            return temp
        elif (typeCode >= 20 and typeCode <= 22):
            temp = ADSB_positional_msg()
            temp.decodeMessage(msgHex[8:22])
            return temp

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


#temp = ADSB_coder()
#temp.initForPlane(5, "FFF321", "YOMAMA", 0, 17)
#encodedIdent = temp.encodeIdentification()
#print(encodedIdent)
#temp.decode(encodedIdent)