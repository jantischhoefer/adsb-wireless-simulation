import numpy as np
from matplotlib import pyplot as plt
from numpy.random import standard_normal
from scipy.stats import rice

import utils


class Transmission:
    def __init__(self, data, src, dest, SNRdB=9, channel_type='rayleigh', carrier_freq=1616000000) -> None:
        self.data = data  # encoded data from src --> dest
        self.src = src  # source id
        self.dest = dest  # destination id
        self.SNRdB = SNRdB  # signal to noise ratio in dB
        self.mod = self._getChannel(channel_type, carrier_freq)  # modulator

    # modulate, channel, demodulate in one function
    def transmit(self):

        modData = self.mod.modulate()

        noisy = self.mod.simChannel(modData)

        demod = self.mod.demodulate(noisy)

        return utils.bit_array_to_hex_string(demod)

    def getData(self) -> str:
        return self.data

    def getSrc(self) -> str:
        return self.src

    def getDest(self) -> str:
        return self.dest

    def _getChannel(self, channel_type, carrier_freq):
        if channel_type == 'rayleigh':
            return BPSK_AWGN_Rayleigh_Channel(utils.hex_string_to_bit_array(self.data), self.SNRdB, carrier_freq)
        elif channel_type == 'rice':
            return BPSK_AWGN_Rice_Channel(utils.hex_string_to_bit_array(self.data), self.SNRdB, carrier_freq)
        else:
            return None


class BPSK_AWGN_Rayleigh_Channel:
    def __init__(self, signal, SNRdB, carrier_freq) -> None:
        self.freq = carrier_freq  # [Hz] carrier frequency
        self.signal = signal
        self.SNRdB = SNRdB
        self.sample_rate = 96
        self.t = np.arange(0, 3 / self.freq, 3 / (self.freq * self.sample_rate))
        self.l = np.arange(0, 3 * 3 / self.freq, 3 / (self.freq * self.sample_rate))
        self.x1 = [np.sin(2 * np.pi * self.freq * ts) for ts in self.t]
        self.x2 = [-np.sin(2 * np.pi * self.freq * ts) for ts in self.t]

    def modulate(self):
        bpsk = []
        for n in range(0, len(self.signal)):
            if self.signal[n] == 1:
                bpsk.extend(self.x1)
            else:
                bpsk.extend(self.x2)
        return np.array(list(bpsk), dtype=float)

    def simChannel(self, signal):
        h_abs = rayleigh(len(signal)) # Rayleigh flat fading samples
        hs = h_abs * signal # fading effect on modulated symbols
        return awgn(self.SNRdB, hs, self.sample_rate) / h_abs # return signal with added awg noise

    def demodulate(self, signal):
        corr1 = 0
        corr2 = 0
        received = []
        for n in range(0, len(self.signal)):
            for i in range(0, self.sample_rate):
                corr1 += self.x1[i] * signal[self.sample_rate * n + i]
                corr2 += self.x2[i] * signal[self.sample_rate * n + i]
            if corr1 > corr2:
                received.append(1)
            else:
                received.append(0)
            corr1 = 0
            corr2 = 0
        return received

    def plot(self, signal, title, x_lbl, y_lbl):
        plt.title(title)
        plt.xlabel(x_lbl)
        plt.ylabel(y_lbl)
        plt.plot(self.l, signal[0:self.l.size])
        plt.show()


class BPSK_AWGN_Rice_Channel:
    def __init__(self, signal, SNRdB, carrier_freq) -> None:
        self.freq = carrier_freq  # [Hz] carrier frequency
        self.signal = signal
        self.SNRdB = SNRdB
        self.sample_rate = 96
        self.t = np.arange(0, 3 / self.freq, 3 / (self.freq * self.sample_rate))
        self.l = np.arange(0, 3 * 3 / self.freq, 3 / (self.freq * self.sample_rate))
        self.x1 = [np.sin(2 * np.pi * self.freq * ts) for ts in self.t]
        self.x2 = [-np.sin(2 * np.pi * self.freq * ts) for ts in self.t]

    def modulate(self):
        bpsk = []
        for n in range(0, len(self.signal)):
            if self.signal[n] == 1:
                bpsk.extend(self.x1)
            else:
                bpsk.extend(self.x2)
        return np.array(list(bpsk), dtype=float)

    def simChannel(self, signal):
        h_abs = rice.rvs(1, len(signal)) # Rice flat fading samples
        hs = h_abs * signal # fading effect on modulated symbols
        return awgn(self.SNRdB, hs, self.sample_rate) / h_abs # return signal with added awg noise

    def demodulate(self, signal):
        corr1 = 0
        corr2 = 0
        received = []
        for n in range(0, len(self.signal)):
            for i in range(0, self.sample_rate):
                corr1 += self.x1[i] * signal[self.sample_rate * n + i]
                corr2 += self.x2[i] * signal[self.sample_rate * n + i]
            if corr1 > corr2:
                received.append(1)
            else:
                received.append(0)
            corr1 = 0
            corr2 = 0
        return received

    def plot(self, signal, title, x_lbl, y_lbl):
        plt.title(title)
        plt.xlabel(x_lbl)
        plt.ylabel(y_lbl)
        plt.plot(self.l, signal[0:self.l.size])
        plt.show()


def awgn(SNRdB, signal, L=1):
    gamma = 10 ** (SNRdB / 10)

    if signal.ndim == 1:
        P = L * sum(abs(signal) ** 2) / len(signal)
    else:
        P = L * sum(sum(abs(signal) ** 2)) / len(signal)

    N0 = P / gamma  # noise spectral density
    if np.isrealobj(signal):
        n = np.sqrt(N0 / 2) * standard_normal(signal.shape)
    else:
        n = np.sqrt(N0 / 2) * (standard_normal(signal.shape) + 1j * standard_normal(signal.shape))
    return signal + n


def rayleigh(N):
    # 1 tap complex gaussian filter
    h = 1 / np.sqrt(2) * (standard_normal(N) + 1j * standard_normal(N))
    return abs(h)


"""
if __name__ == '__main__':
    sample_data = '10a45691824da534bc90ff2a3cde'.upper()
    print(sample_data)
    t = Transmission(sample_data, 'a360', 's-32', 15, 'rice')
    transmitted = t.transmit()
    print(transmitted)
"""

"""
Inspiration from paper: https://journals.vgtu.lt/index.php/Aviation/article/download/3574/3001
Iridium satellite model:
- three phased array antennas
- 1616-1626.5 MHz
Channel:
- hybrid Time Division Multiple Access / Frequency Division Multiple Access
- Time Division Duplex 90ms frame
- BPSK modulation scheme
"""
