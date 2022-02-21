def hex_string_to_bit_array(hex_string):
    result = []
    bits = bin(int(hex_string, 16))[2:]
    result.extend([int(b) for b in bits])
    return result

def bit_array_to_hex_string(bit_arr):
    return hex(int(''.join(str(b) for b in bit_arr), 2))[2:].upper()

def adsb_int_to_char(int_val):
    if int_val == 1: return 'A'
    if int_val == 2: return 'B'
    if int_val == 3: return 'C'
    if int_val == 4: return 'D'
    if int_val == 5: return 'E'
    if int_val == 6: return 'F'
    if int_val == 7: return 'G'
    if int_val == 8: return 'H'
    if int_val == 9: return 'I'
    if int_val == 10: return 'J'
    if int_val == 11: return 'K'
    if int_val == 12: return 'L'
    if int_val == 13: return 'M'
    if int_val == 14: return 'N'
    if int_val == 15: return 'O'
    if int_val == 16: return 'P'
    if int_val == 17: return 'Q'
    if int_val == 18: return 'R'
    if int_val == 19: return 'S'
    if int_val == 20: return 'T'
    if int_val == 21: return 'U'
    if int_val == 22: return 'V'
    if int_val == 23: return 'W'
    if int_val == 24: return 'X'
    if int_val == 25: return 'Y'
    if int_val == 26: return 'Z'
    if int_val == 32: return ' '
    if int_val == 48: return '0'
    if int_val == 49: return '1'
    if int_val == 50: return '2'
    if int_val == 51: return '3'
    if int_val == 52: return '4'
    if int_val == 53: return '5'
    if int_val == 54: return '6'
    if int_val == 55: return '7'
    if int_val == 56: return '8'
    if int_val == 57: return '9'
    return '#'

def adsb_char_to_int(char):
    char = str.upper(char)
    if char == 'A': return 1
    if char == 'B': return 2
    if char == 'C': return 3
    if char == 'D': return 4
    if char == 'E': return 5
    if char == 'F': return 6
    if char == 'G': return 7
    if char == 'H': return 8
    if char == 'I': return 9
    if char == 'J': return 10
    if char == 'K': return 11
    if char == 'L': return 12
    if char == 'M': return 13
    if char == 'N': return 14
    if char == 'O': return 15
    if char == 'P': return 16
    if char == 'Q': return 17
    if char == 'R': return 18
    if char == 'S': return 19
    if char == 'T': return 20
    if char == 'U': return 21
    if char == 'V': return 22
    if char == 'W': return 23
    if char == 'X': return 24
    if char == 'Y': return 25
    if char == 'Z': return 26
    if char == ' ': return 32
    if char == '0': return 48
    if char == '1': return 49
    if char == '2': return 50
    if char == '3': return 51
    if char == '4': return 52
    if char == '5': return 53
    if char == '6': return 54
    if char == '7': return 55
    if char == '8': return 56
    if char == '9': return 57
    return 32