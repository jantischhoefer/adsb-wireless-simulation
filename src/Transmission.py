import math
import numpy as np
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
        if mod_type == 'bpsk': return BPSK(self.freq, self.data, self.snr)
        else: return None


class BPSK:
    def __init__(self, freq, signal, snr) -> None:
        self.freq = freq
        self.signal = signal
        self.snr = snr
        self.t = np.arange(0, 3/freq, 3/(freq*48))
        self.l = np.arange(0, 3*3/freq, 3/(freq*48))
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

    def noise(self, signal):
        # channel impulse response - maybe design new channel!
        h = [1,0,0.8,0,0.6,0,0,0.4]
        sig_avg_watts = np.mean(signal**2)
        sig_avg_db = 10 * np.log10(sig_avg_watts)
        noise_avg_db = sig_avg_db - self.snr
        noise_avg_watts = 10 ** (noise_avg_db / 10)
        mean_noise = 0
        n = np.random.normal(mean_noise, np.sqrt(noise_avg_watts), len(signal) + len(h) - 1)
        return np.convolve(signal, h) + n

    def awgn(self, signal, L=1):
        gamma = 10 ** (self.snr/10)

        if signal.ndim==1:
            P = L*sum(abs(signal)**2)/len(signal)
        else:
            P = L*sum(sum(abs(signal)**2))/len(signal)
        
        N0 = P / gamma # noise spectral density
        if np.isrealobj(signal):
            n = np.sqrt(N0/2)*np.random.standard_normal(signal.shape)
        else:
            n = np.sqrt(N0/2)*(np.random.standard_normal(signal.shape)+1j*np.random.standard_normal(signal.shape))
        return signal + n

    def generate_square_matrix(self, arr_data, filter_size, isComplex):
        highest_value_index = arr_data.argmax()
        sqMat = np.mat(np.zeros(shape=(filter_size,filter_size)))
        if (isComplex):
            sqMat = sqMat.astype(complex)
        for i in range(filter_size):
            for j in range(filter_size):
                currentIndex = j + highest_value_index - i
                if ((currentIndex < 0) or (currentIndex >= len(arr_data))):
                    sqMat[j,i] = 0
                else:
                    sqMat[j,i] = arr_data[currentIndex]
        return sqMat
        

    def MMSE_equalizer(self, x, y, filter_size):
        ryy = np.correlate(y, y, 'full')
        rxy = np.correlate(x, y, 'full')

        Ryy = self.generate_square_matrix(ryy, filter_size, True)
        Rxy = np.mat(np.zeros(shape=(filter_size, 1)))

        offset = (len(rxy)-filter_size)>>1
        for i in range(filter_size):
            Rxy[i, 0] = rxy[i + offset]
        MMSE_C_VEC = np.asarray(np.linalg.inv(Ryy)* Rxy).flatten()
        return MMSE_C_VEC

    def reduce_to_filter_length(arr, filter_length):
        left = filter_length>>1
        return arr[left:left+filter_length]

    def receive(self, signal):
        xp = np.random.randint(0, 10, len(signal))
        yp = self.noise(xp)
        cvec = self.MMSE_equalizer(xp, yp)
        z = np.convolve(yp, cvec)
        z = self.reduce_to_filter_length(z, len(xp))

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
    t = Transmission(d, 'a360', 's-32', 1616000000, 'bpsk', 10)
    mod_data = t.mod.modulate()
    noisy = t.mod.noise(mod_data)
    nawgn = t.mod.awgn(mod_data)
    t.mod.plot(mod_data, 'mod', 'v', 't')
    t.mod.plot(noisy, 'noisy signal', 'v', 't')
    t.mod.plot(nawgn, 'awgn', 'v', 't')
    #print(sample_data)
    #print(utils.bit_array_to_hex_string(t.getData()))
#"""

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
