import numpy as np
from matplotlib import pyplot as plt
from numpy.random import standard_normal
from scipy.stats import rice

import utils

class Transmission:
    """
    A class used to represent a Transmission between transmitter and receiver
    
    Attributes
    ----------
    data : str
        a hexadecimal string encoded by ADS-B encoder
    src : str
        id of the source / transmitter
    src_is_satellite : bool
        boolean indicating if the source id is a satellite
    dest : str
        id of the destination / receiver
    SNRdB : int
        signal to noise ratio in [dB] indicating the quality of the transmission
    channel : Channel
        Channel class that has to be implemented inside the Transmission class.
        Currently implemented: BPSK_AWGN_Rayleigh_Channel | BPSK_AWGN_Rician_Channel
    
    Methods
    -------
    transmit()
        performs modulation, channel simulation (fading + noise) and demodulation
    getData() -> str
        returns the input hexadecimal string
    getSrc() -> str
        returns the source / transmitter id
    getDest() -> str
        returns the destination / receiver id
    _getChannel(channel_model: str, carrier_frequency: int) -> Channel
        constructs and returns an implemented channel model selected by
        channel_model and the carrier_frequency

    """
    def __init__(self, 
                data, 
                src, 
                src_is_satellite, 
                dest,
                SNRdB=9, 
                channel_model='bpsk-awgn-rayleigh',
                carrier_frequency=1616000000) -> None:
        """
        Parameters
        ----------
        data : str
            a hexadecimal string encoded by ADS-B encoder
        src : str
            id of the source / transmitter
        src_is_satellite : bool
            boolean indicating if the source id is a satellite
        dest : str
            id of the destination / receiver
        SNRdB : int
            signal to noise ratio in [dB] indicating the quality of the transmission
        channel_model : str
            chooses the used fading channel model.
            'bpsk-awgn-rayleigh' | 'bpsk-awgn-rice'
        carrier_frequency : int
            Carrier frequency of the modulation in [Hz]
        channel : Channel
            Modulator class that has to be implemented inside the Transmission class.
            Currently implemented: BPSK_AWGN_Rayleigh_Channel | BPSK_AWGN_Rician_Channel
        """

        self.data = data
        self.src = src  # source id
        self.src_is_satellite = src_is_satellite
        self.dest = dest  # destination id
        self.SNRdB = SNRdB  # signal to noise ratio in dB
        self.channel = self._getChannel(channel_model, carrier_frequency)  # modulator

    def transmit(self):
        """
        Performs one transmission cycle including modulation, channel simulation
        (fading and noise) and demodulation to simulate the transmission.
        """

        modulated_data = self.channel.modulate()
        noisy_data = self.channel.simulateChannel(modulated_data)
        demodulated_data = self.channel.demodulate(noisy_data)
        return utils.bit_array_to_hex_string(demodulated_data)

    def getData(self) -> str:
        return self.data

    def getSrc(self) -> str:
        return self.src

    def getDest(self) -> str:
        return self.dest

    def _getChannel(self, channel_model, carrier_frequency):
        """
        Constructs and returns an implemented channel model.

        Parameters
        ----------
        channel_model : str
            Name of an implemented channel model
        carrier_frequency : int
            Carrier frequency used by the modulation in [Hz]

        Returns
        -------
            Implemented Channel model
        """

        if channel_model == 'bpsk-awgn-rayleigh':
            return BPSK_AWGN_Rayleigh_Channel(utils.hex_string_to_bit_array(self.data), self.SNRdB, carrier_frequency)
        elif channel_model == 'bpsk-awgn-rice':
            return BPSK_AWGN_Rician_Channel(utils.hex_string_to_bit_array(self.data), self.SNRdB, carrier_frequency)
        else:
            return None


class BPSK_AWGN_Rayleigh_Channel:
    """
    Implemented Channel class model using Binary Phase Shift Keying modulation,
    Rayleigh fading channel and Additive White Gaussian Noise

    Attributes
    ----------
    data : list(int)
        list of bits, converted hexadecimal string using ref(utils.hex_string_to_bit_array(...))
    SNRdB : int
        signal to noise ratio in [dB] indicating the quality of the transmission
    carrier_frequency : int
        Carrier frequency of the modulation in [Hz]
    sample_rate : int
        Resolution of the sampled sine wave
    t : np.array
        time steps of one sine cycle
    l : np.array
        three time steps
    sine_0_phase : list
        sampled sine phase with 0° phase
    sine_180_phase : list
        sampled sine phase with 180° phase

    Methods
    -------
    modulate() -> list(int)
        Modulate data with the implemented modulation technique => Binary phase shift keying.
    simulateChannel(signal : list(int)) -> list(int)
        Simulates the transmission over a channel.
        Adds Rayleigh distribution as fading and noise.
    demodulate(signal : list(int)) -> list(int)
        Demodulates the data with implemented modulation technique => Binary phase shift keying.
    _plot(signal : list(int), title : str, x_lbl : str, y_lbl : str)
        Small helper function for faster plotting.
    """

    def __init__(self, data, SNRdB, carrier_frequency):
        """
        Parameters
        ----------
        data : list(int)
            list of bits, converted hexadecimal string using ref(utils.hex_string_to_bit_array(...))
        SNRdB : int
            signal to noise ratio in [dB] indicating the quality of the transmission
        carrier_frequency : int
            Carrier frequency of the modulation in [Hz]
        """

        self.data = data
        self.SNRdB = SNRdB
        self.carrier_frequency = carrier_frequency
        self.sample_rate = 48
        self.t = np.arange(0, 3 / self.carrier_frequency, 3 / (self.carrier_frequency * self.sample_rate))
        self.l = np.arange(0, 3 * 3 / self.carrier_frequency, 3 / (self.carrier_frequency * self.sample_rate))
        self.sine_0_phase = [np.sin(2 * np.pi * self.carrier_frequency * ts) for ts in self.t]
        self.sine_180_phase = [-np.sin(2 * np.pi * self.carrier_frequency * ts) for ts in self.t]

    def modulate(self):
        """
        Modulates the data with the implemented modulation technique => BPSK

        Returns
        -------
        list
            list of floats of the modulated signal
        """

        modulated_signal = []
        for n in range(0, len(self.data)):
            if self.data[n] == 1:
                modulated_signal.extend(self.sine_0_phase)
            else:
                modulated_signal.extend(self.sine_180_phase)
        return np.array(list(modulated_signal), dtype=float)

    def simulateChannel(self, signal):
        """
        Simulates the transmission over a channel.
        Adds fading and noise.

        Parameters
        ----------
        signal : list(float)
            Modulated signal

        Returns
        -------
        list
            list of floats of the faded noisy signal
        """

        h_abs = rayleigh(len(signal)) # Rayleigh flat fading samples
        hs = h_abs * signal # fading effect on modulated symbols
        return awgn(self.SNRdB, hs) / h_abs # return signal with added awg noise

    def demodulate(self, signal):
        """
        Demodulates the data with implemented modulation technique => BPSK

        Parameters
        ----------
        signal : list(float)
            received signal to apply demodulation
        
        Returns
        -------
        list
            list of ints / bits of the demodulated signal
        """

        corr1 = 0
        corr2 = 0
        demodulated_data = []
        for n in range(0, len(self.data)):
            for i in range(0, self.sample_rate):
                corr1 += self.sine_0_phase[i] * signal[self.sample_rate * n + i]
                corr2 += self.sine_180_phase[i] * signal[self.sample_rate * n + i]
            if corr1 > corr2:
                demodulated_data.append(1)
            else:
                demodulated_data.append(0)
            corr1 = 0
            corr2 = 0
        return demodulated_data

    def _plot(self, signal, title, x_lbl, y_lbl):
        plt.title(title)
        plt.xlabel(x_lbl)
        plt.ylabel(y_lbl)
        plt.plot(self.l, signal[0:self.l.size])
        plt.show()


class BPSK_AWGN_Rician_Channel:
    """
    Implemented Channel class model using Binary Phase Shift Keying modulation,
    Rician fading channel and Additive White Gaussian Noise

    Attributes
    ----------
    data : list(int)
        list of bits, converted hexadecimal string using ref(utils.hex_string_to_bit_array(...))
    SNRdB : int
        signal to noise ratio in [dB] indicating the quality of the transmission
    carrier_frequency : int
        Carrier frequency of the modulation in [Hz]
    sample_rate : int
        Resolution of the sampled sine wave
    t : np.array
        time steps of one sine cycle
    l : np.array
        three time steps
    sine_0_phase : list
        sampled sine phase with 0° phase
    sine_180_phase : list
        sampled sine phase with 180° phase

    Methods
    -------
    modulate() -> list(int)
        Modulate data with the implemented modulation technique => Binary phase shift keying.
    simulateChannel(signal : list(int)) -> list(int)
        Simulates the transmission over a channel.
        Adds rician distribution as fading and noise.
    demodulate(signal : list(int)) -> list(int)
        Demodulates the data with implemented modulation technique => Binary phase shift keying.
    _plot(signal : list(int), title : str, x_lbl : str, y_lbl : str)
        Small helper function for faster plotting.
    """

    def __init__(self, data, SNRdB, carrier_frequency):
        """
        Parameters
        ----------
        data : list(int)
            list of bits, converted hexadecimal string using ref(utils.hex_string_to_bit_array(...))
        SNRdB : int
            signal to noise ratio in [dB] indicating the quality of the transmission
        carrier_frequency : int
            Carrier frequency of the modulation in [Hz]
        """

        self.data = data
        self.SNRdB = SNRdB
        self.carrier_frequency = carrier_frequency
        self.sample_rate = 48
        self.t = np.arange(0, 3 / self.carrier_frequency, 3 / (self.carrier_frequency * self.sample_rate))
        self.l = np.arange(0, 3 * 3 / self.carrier_frequency, 3 / (self.carrier_frequency * self.sample_rate))
        self.sine_0_phase = [np.sin(2 * np.pi * self.carrier_frequency * ts) for ts in self.t]
        self.sine_180_phase = [-np.sin(2 * np.pi * self.carrier_frequency * ts) for ts in self.t]

    def modulate(self):
        """
        Modulates the data with the implemented modulation technique => BPSK

        Returns
        -------
        list
            list of floats of the modulated signal
        """

        modulated_signal = []
        for n in range(0, len(self.data)):
            if self.data[n] == 1:
                modulated_signal.extend(self.sine_0_phase)
            else:
                modulated_signal.extend(self.sine_180_phase)
        return np.array(list(modulated_signal), dtype=float)

    def simulateChannel(self, signal):
        """
        Simulates the transmission over a channel.
        Adds Rician distribution as fading and noise.

        Parameters
        ----------
        signal : list(float)
            Modulated signal

        Returns
        -------
        list
            list of floats of the faded noisy signal
        """

        h_abs = rice.rvs(1, len(signal)) # Rice flat fading samples
        hs = h_abs * signal # fading effect on modulated symbols
        return awgn(self.SNRdB, hs) / h_abs # return signal with added awg noise

    def demodulate(self, signal):
        """
        Demodulates the data with implemented modulation technique => BPSK

        Parameters
        ----------
        signal : list(float)
            received signal to apply demodulation
        
        Returns
        -------
        list
            list of ints / bits of the demodulated signal
        """

        corr1 = 0
        corr2 = 0
        demodulated_data = []
        for n in range(0, len(self.data)):
            for i in range(0, self.sample_rate):
                corr1 += self.sine_0_phase[i] * signal[self.sample_rate * n + i]
                corr2 += self.sine_180_phase[i] * signal[self.sample_rate * n + i]
            if corr1 > corr2:
                demodulated_data.append(1)
            else:
                demodulated_data.append(0)
            corr1 = 0
            corr2 = 0
        return demodulated_data

    def plot(self, signal, title, x_lbl, y_lbl):
        plt.title(title)
        plt.xlabel(x_lbl)
        plt.ylabel(y_lbl)
        plt.plot(self.l, signal[0:self.l.size])
        plt.show()


def awgn(SNRdB, signal, L=1):
    """
    Additive White Gaussian Noise (AWGN) channel

    Add AWGN noise to input signal.

    Parameters
    ----------
    SNRdB : int
        desired signal to noise ratio in [dB] for the received signal
    signal : list(float)
        input / transmitted signal vector
    L : int
        oversampling factor (applicable for waveform simulation)
        default L = 1
    
    Returns
    -------
    list
        list of floats with the added noise
    """

    gamma = 10 ** (SNRdB / 10)
    if signal.ndim == 1:
        P = L*10 * sum(abs(signal) ** 2) / len(signal)
    else:
        P = L*10 * sum(sum(abs(signal) ** 2)) / len(signal)
    N0 = P / gamma  # noise spectral density
    if np.isrealobj(signal):
        n = np.sqrt(N0 / 2) * standard_normal(signal.shape)
    else:
        n = np.sqrt(N0 / 2) * (standard_normal(signal.shape) + 1j * standard_normal(signal.shape))
    return signal + n


def rayleigh(N):
    """
    Generate Rayleigh flat-fading channel samples.

    Parameters
    ----------
    N : int
        number of samples to generate
    
    Returns
    -------
    abs_h
        Rayleigh flat fading samples
    """

    # 1 tap complex gaussian filter
    h = 1 / np.sqrt(2) * (standard_normal(N) + 1j * standard_normal(N))
    return abs(h)
