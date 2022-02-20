def hex_string_to_bit_array(hex_string):
    result = []
    bits = bin(int(hex_string, 16))[2:]
    result.extend([int(b) for b in bits])
    return result

def bit_array_to_hex_string(bit_arr):
    return hex(int(''.join(str(b) for b in bit_arr), 2))[2:]
