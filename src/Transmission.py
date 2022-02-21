import math
import numpy as np
from numpy.random import standard_normal
from matplotlib import pyplot as plt
from matplotlib.pyplot import xlabel, ylabel, title, grid, show

import utils

class Transmission:
    def __init__(self, data, src, dest, freq, mod_type, snr) -> None:
        # modulated data (according to protocol) that is sent from src to dest
        self.data = data
        # source id
        self.src = src
        # destination id
        self.dest = dest
        # carrier frequency
        self.freq = freq
        # signal to noise ratio
        self.snr = snr
        # modulator
        self.mod = self.getModulator(mod_type)

    # modulate the encoded self.data with self.mod_type
    def modulate(self):
        return self.mod.modulate()

    
    # add noise to self.data to simulate a transmission
    def noise(self) -> None:
        #snr_linear = dB2Linear(self.snr)
        #noise_power = 1 / snr_linear
        #n = math.sqrt(noise_power) * randn_c(self.data.size)
        pass
        # self.data = self.data + n

    # demodulate the encoded self.data with self.mod_type
    def demodulate(self) -> None:
        self.data = self.mod.demodulate(self.data)

    def transmit(self) -> None:
        self.modulate()
        self.noise()
        self.demodulate()

    def getData(self) -> str:
        return self.data

    def getModulator(self, mod_type):
        if mod_type == 'bpsk': return BpskAwgnRayleighModulator(self.freq, self.data, self.snr)
        else: return None


class BpskAwgnRayleighModulator:
    def __init__(self, freq, signal, snr) -> None:
        self.freq = freq
        self.signal = signal
        self.snr = snr
        self.t = np.arange(0, 3/freq, 3/(freq*96))
        self.l = np.arange(0, 3*3/freq, 3/(freq*96))
        self.x1 = [np.sin(2*np.pi*freq*ts) for ts in self.t]
        self.x2 = [-np.sin(2*np.pi*freq*ts) for ts in self.t]

    def modulate(self):
        bpsk = []
        for n in range(0, len(self.signal)):
            if self.signal[n] == 1:
                bpsk.extend(self.x1)
            else:
                bpsk.extend(self.x2)
        return np.array(list(bpsk), dtype=float)

    def awgn(self, signal, L=1):
        gamma = 10**(self.snr/10)

        if signal.ndim==1:
            P = L*sum(abs(signal)**2)/len(signal)
        else:
            P = L*sum(sum(abs(signal)**2))/len(signal)
        
        N0 = P / gamma # noise spectral density
        if np.isrealobj(signal):
            n = np.sqrt(N0/2)*standard_normal(signal.shape)
        else:
            n = np.sqrt(N0/2)*(standard_normal(signal.shape)+1j*standard_normal(signal.shape))
        return signal + n

    def rayleigh(self, N):
        # 1 tap complex gaussian filter
        h = 1/np.sqrt(2)*(standard_normal(N)+1j*standard_normal(N))
        return abs(h)

    def receive(self, signal):
        h_abs = self.rayleigh(len(signal)) # Rayleigh flat fading samples
        hs = h_abs * signal # fading effect on modulated symbols
        return self.awgn(hs)

    def demodulate(self, signal):
        corr1 = 0
        corr2 = 0
        received = []
        for n in range(0, len(self.signal)):
            for i in range(0,96):
                corr1 += self.x1[i]*signal[96*n + i]
                corr2 += self.x2[i]*signal[96*n + i]
            if corr1 > corr2:
                received.append(1)
            else: received.append(0)
            corr1 = 0
            corr2 = 0
        return received

    def plot(self, signal, title, x_lbl, y_lbl):
        plt.title(title)
        plt.xlabel(x_lbl)
        plt.ylabel(y_lbl)
        plt.plot(self.l, signal[0:self.l.size])
        plt.show()


#"""
if __name__ == '__main__':
    sample_data = '10a45691824da534bc90ff2a3cde'
    d = np.array(utils.hex_string_to_bit_array(sample_data))
    t = Transmission(d, 'a360', 's-32', 1616000000, 'bpsk', 5)
    mod_data = t.mod.modulate()
    rayleighAwgn = t.mod.receive(mod_data)
    demod = t.mod.demodulate(rayleighAwgn)
    t.mod.plot(mod_data, 'mod', 'v', 't')
    t.mod.plot(rayleighAwgn, 'noise', 'v', 't')
    print(sample_data)
    print("Demod len: "+ str(len(demod)))
    print(utils.bit_array_to_hex_string(demod))
    #print(sample_data)
    #print(utils.bit_array_to_hex_string(t.getData()))
#"""

"""
print("len(t): " + str(len(t.mod.t)))
    print("len(l): " + str(len(t.mod.l)))

    print("bits:")
    print(d)
    print("len(bits): " + str(len(d)))
    print("mod:")
    print(mod_data)
    print("len(mod): " + str(len(mod_data)))
"""

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
