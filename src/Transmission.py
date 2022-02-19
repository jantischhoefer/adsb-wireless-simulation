class Transmission:
    def __init__(self, data, src, dest):
        # modulated data (according to protocol) that is sent from src to dest
        self.data = data
        # source id
        self.src = src
        # destination id
        self.dest = dest

    def modulate():
        pass

    def demodulate():
        pass

    def noise():
        pass
        
if __name__ == '__main__':
    print("Transmission running...")

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