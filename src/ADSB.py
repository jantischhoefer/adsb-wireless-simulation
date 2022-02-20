import utils
import math

# can encode, decode and print the message part of an ADSB position transmission
class ADSB_positional_msg:
    rawMSGbin = ""
    downlinkFormat = 0
    transponderCapability = 0
    ICAOaddress = ""
    typeCode = 0
    altitudeSource = ""
    surveillanceStatus = 0
    singleAntennaFlag = 0
    altitude = 0
    time = 0
    cprFormat = 0
    latCPR = 0
    lonCPR = 0

    def __init__(self, downlinkFormat, transponderCapability, ICAOaddress):
        self.downlinkFormat = downlinkFormat
        self.transponderCapability = transponderCapability
        self.ICAOaddress = ICAOaddress

    def calculateNL(self, lat):
        nZ = 15
        if lat == 0:
            return 59
        elif lat == 87 or lat == -87:
            return 2
        elif lat > 87 or lat < -87:
            return 1
        else:
            return math.floor(2 * math.pi / (math.acos(1 - (1 - math.cos(math.pi / (2 * nZ))) / (pow(math.cos(math.pi / 180 * lat), 2)))))

    def decodeMessage(self, msg):
        msgBin = bin(int(msg, 16))[2:]
        # determine wether altitude is barometric or from GNSS
        self.typeCode = int(msgBin[0:5], 2)

        # determine surveillance status
        self.surveillanceStatus = int(msgBin[5:7], 2)

        # single antenna flag
        self.singleAntennaFlag = int(msgBin[7], 2)

        # determine altitude
        altiBin = msgBin[7:19]
        if altiBin[7] == '1':
            self.altitude = 25 * (int(altiBin[:7] + altiBin[8:], 2)) - 1000
        else:
            self.altitude = 100 * (int(altiBin[:7] + altiBin[8:], 2)) - 1000
        # convert altitude to m
        self.altitude /= 3.281

        # altitude source
        if self.typeCode < 20:
            self.altitudeSource = "Barometric"
        else:
            self.altitudeSource = "GNSS"

        #timeflag
        self.time = int(msgBin[19], 2)

        #CPR format
        self.cprFormat = int(msgBin[20], 2)

        # latitude and longitude (CPR format)
        self.latCPR = int(msgBin[21:38], 2) / pow(2, 17)
        self.lonCPR = int(msgBin[38:55], 2) / pow(2, 17)

        return self

    # determine the real position of plane with given ICAO based on old messages
    def determineTruePosition(self, ICAOaddress, messages):
        # first, determine if latest message was even or odd
        latCPReven = 0
        latCPRodd = 0
        lonCPReven = 0
        lonCPRodd = 0
        Teven = 0
        Todd = 0
        messageFound = False
        # find last messages that was odd if current one is even and vice versa
        if(messages[-1].cprFormat == 0):
            latCPReven = messages[-1].latCPR
            lonCPReven = messages[-1].lonCPR
            Teven = messages[-1].time
        else:
            latCPRodd = messages[-1].latCPR
            lonCPRodd = messages[-1].lonCPR
            Todd = messages[-1].time
        for msg in reversed(messages):
            if msg.ICAOaddress == ICAOaddress and msg.cprFormat != messages[-1].cprFormat:
                if (messages[-1].cprFormat == 0):
                    latCPRodd = msg.latCPR
                    lonCPRodd = msg.lonCPR
                    Todd = msg.time
                else:
                    latCPReven = msg.latCPR
                    lonCPReven = msg.lonCPR
                    Teven = msg.time
                messageFound = True
                break
        if(messageFound == False):
            print ("Not enough data available to determine accurate position.")
            return

        # calculate actual lat and lon
        nZ = 15
        dLateven = 360/(4*nZ)
        dLatodd = 360 / (4 * nZ - 1)
        j = math.floor(59*latCPReven-60*latCPRodd + 0.5)
        latEven = dLateven * (j%60+latCPReven)
        latOdd = dLatodd * (j%59+latCPRodd)
        if (latEven >= 270): latEven = latEven - 360
        if (latOdd >= 270): latOdd = latOdd - 360
        if (self.calculateNL(latEven) != self.calculateNL(latOdd)):
            print("Messages not from same longitude zone; Position calculation not possible")
            return

        latitude = 0
        if Teven >= Todd:
            latitude = latEven
        else:
            latitude = latOdd

        m = math.floor(lonCPReven * (self.calculateNL(latitude)-1)-lonCPRodd*self.calculateNL(latitude)+0.5)
        neven = 1
        nodd = 1
        if self.calculateNL(latitude) > 1:
            neven = self.calculateNL(latitude)
        if self.calculateNL(latitude-1) > 1:
            nodd = self.calculateNL(latitude - 1)
        dLoneven = 360/neven
        dLonodd = 360/nodd
        lonEven = dLoneven*(m%neven + lonCPReven)
        lonodd = dLonodd * (m % nodd + lonCPRodd)

        longitude = 0
        if Teven >= Todd:
            longitude = lonEven
        else:
            longitude = lonodd
        if longitude >= 180:
            longitude = longitude - 360

        print("Decoded Longitude: ", longitude, "\nDecoded Latitude: ", latitude)

    def encodeMessage(self, surveillanceStatus, singleAntennaFlag, altitude, time, cprFormat, latitude, longitude):
        return ""

    def printMessage(self):
        dataStr = ""
        dataStr += "Downlink Format: " + str(self.downlinkFormat) + "\n"
        dataStr += "Transponder Capability: " + str(self.transponderCapability) + "\n"
        dataStr += "ICAO Address: " + str(self.ICAOaddress) + "\n"
        dataStr += "Type Code: " + str(self.typeCode) + "\n"
        dataStr += "Surveillance Status: " + str(self.surveillanceStatus) + "\n"
        dataStr += "Single Antenna: " + str(self.singleAntennaFlag) + "\n"
        dataStr += "CPR Format and Time Flag: " + str(self.cprFormat) + " " + str(self.time) + "\n"
        dataStr += "Altitude: " + str(self.altitude) + "(" + self.altitudeSource + ")\n"
        dataStr += "Latitude (CPR): " + str(self.latCPR) + "\n"
        dataStr += "Longitude (CPR): " + str(self.lonCPR) + "\n"
        print(dataStr)


# can encode, decode and print the message part of an ADSB identification transmission
class ADSB_identification_msg:
    rawMSGbin = ""
    downlinkFormat = 0
    transponderCapability = 0
    ICAOaddress = ""
    typeCode = 0
    vortexCategory = 0
    callSign = ""

    def __init__(self, downlinkFormat, transponderCapability, ICAOaddress):
        self.downlinkFormat = downlinkFormat
        self.transponderCapability = transponderCapability
        self.ICAOaddress = ICAOaddress

    def decodeMessage(self, msg):
        msgBin = bin(int(msg, 16))
        self.typeCode = int(msgBin[0:5], 2)
        self.vortexCategory = int(msgBin[5:8], 2)

        # callSign
        for i in range(8):
            self.callSign += utils.adsb_int_to_char(int(msgBin[8 + i*6:8+i*6+6], 2))

        return self

    def encodeMessage(self, vortexCategory, callSign, typeCode):

        self.vortexCategory = vortexCategory
        self.callSign = callSign
        self.typeCode = typeCode

        # type code
        typeCodeBits = bin(typeCode)[2:]
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

    def printMessage(self):
        dataStr = ""
        dataStr += "Downlink Format: " + str(self.downlinkFormat) + "\n"
        dataStr += "Transponder Capability: " + str(self.transponderCapability) + "\n"
        dataStr += "ICAO Address: " + str(self.ICAOaddress) + "\n"
        dataStr += "Type Code: " + str(self.typeCode) + "\n"
        dataStr += "Vortex Category: " + str(self.vortexCategory) + "\n"
        dataStr += "Callsign: " + str(self.callSign) + "\n"
        print(dataStr)

class ADSB_coder:

    # lists for decoded messages
    decPosMSGS = []
    decIdentMSGS = []

    # lists for encoded messages
    encPosMSGS = []
    encIdentMSGS = []

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
            identMSG = ADSB_identification_msg(downlinkFormat, transponderCapability, ICAOaddress)
            identMSG.rawMSGbin = bin(int(msgHex, 16))
            identMSG.decodeMessage(msgHex[8:22])
            print("Identification-message received.")
            identMSG.printMessage()
            self.decIdentMSGS.append(identMSG)
        elif (typeCode >= 9 and typeCode <= 18) or (typeCode >= 20 and typeCode <= 22):
            # position message
            posMSG = ADSB_positional_msg(downlinkFormat, transponderCapability, ICAOaddress)
            posMSG.rawMSGbin = bin(int(msgHex, 16))
            posMSG.decodeMessage(msgHex[8:22])
            print("Position-message received.")
            posMSG.printMessage()
            self.decPosMSGS.append(posMSG)
            posMSG.determineTruePosition(ICAOaddress, self.decPosMSGS)

    # encode message prefix containing downlink format and transponder capability
    def encodeADSBprefix(self, downlinkFormat, transponderCapability, ICAOaddress):
        dFcTbin = bin((downlinkFormat<<3) | transponderCapability)[2:]
        ICAObin = bin(int(ICAOaddress, 16))[2:]
        while len(ICAObin) < 24:
            ICAObin = "0" + ICAObin
        return hex(int(dFcTbin + ICAObin, 2)).upper()

    def encodePosition(self, surveillanceStatus, singleAntennaFlag, altitude, time, cprFormat, latitude, longitude):
        ADSB_positional_msg.encodeMessage(surveillanceStatus, singleAntennaFlag, altitude, time, cprFormat, latitude, longitude)

    def encodeIdentification(self, downlinkFormat, transponderCapability, ICAOaddress, vortexCategory, callSign, typeCode = 0):
        prefix = self.encodeADSBprefix(downlinkFormat, transponderCapability, ICAOaddress)[2:]
        identMSG = ADSB_identification_msg(downlinkFormat, transponderCapability, ICAOaddress)
        msgPart = identMSG.encodeMessage(vortexCategory, callSign, typeCode)[2:]
        crc = self.calculateCRC(prefix + msgPart)
        identMSG.rawMSGbin = bin(int(prefix + msgPart + crc, 16))
        self.encIdentMSGS.append(identMSG)
        return (prefix + msgPart + crc).upper()


#temp = ADSB_coder()
#temp.decode("8D40621D58C386435CC412692AD6")
#temp.decode("8D40621D58C382D690C8AC2863A7")