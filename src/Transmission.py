import math
import numpy as np

from pyphysim.modulators.fundamental import BPSK
from pyphysim.util.conversion import dB2Linear
from pyphysim.util.misc import randn_c

import utils

class Transmission:
    def __init__(self, data, src, dest, mod_type, snr) -> None:
        # modulated data (according to protocol) that is sent from src to dest
        self.data = data
        # source id
        self.src = src
        # destination id
        self.dest = dest
        # modulation type - BPSK()
        self.mod_type = mod_type
        # signal to noise ratio
        self.snr = snr

    # modulate the encoded self.data with self.mod_type
    def modulate(self) -> None:
        self.data = self.mod_type.modulate(self.data)    

    # add noise to self.data to simulate a transmission
    def noise(self) -> None:
        snr_linear = dB2Linear(self.snr)
        noise_power = 1 / snr_linear
        n = math.sqrt(noise_power) * randn_c(self.data.size)
        self.data = self.data + n

    # demodulate the encoded self.data with self.mod_type
    def demodulate(self) -> None:
        self.data = self.mod_type.demodulate(self.data)

    def transmit(self) -> None:
        self.modulate()
        self.noise()
        self.demodulate()

    def getData(self) -> str:
        return self.data

if __name__ == '__main__':
    sample_data = '10a45691824da534bc90ff2a3cde'
    d = np.array(utils.hex_string_to_bit_array(sample_data))
    t = Transmission(d, 'a360', 's-32', BPSK(), 10)
    t.transmit()
    print(sample_data)
    print(utils.bit_array_to_hex_string(t.getData()))

# jeder Teilnehmer hat ID
#   - Flugzeug hat Flugnummer
#   - GS hat Flughafenkennung
#   - Satellit hat "s-nr"
# diese ID wird als src oder dest eingetragen in Transmission

"""
Paper: https://journals.vgtu.lt/index.php/Aviation/article/download/3574/3001
Iridium satellite model:
- three phased array antennas
- 1616-1626.5 MHz
Channel:
- hybrid Time Division Multiple Access / Frequency Division Multiple Access
- Time Division Duplex 90ms frame
- BPSK modulation scheme
"""
