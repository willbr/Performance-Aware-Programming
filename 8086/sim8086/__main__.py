from sys import argv
from struct import (
        unpack_from,
        )

register_field_encoding = [
        [ 'AL', 'CL', 'DL', 'BL', 'AH', 'CH', 'DH', 'BH'], #  8-bit
        [ 'AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI'], # 16-bit
        ]


mode_field_encoding = {
        0b00: 'Memory Mode, no displacement follows',
        0b01: 'Memory Mode, 8-bit displacement follows',
        0b10: 'Memory Mode, 16-bit displacement follows',
        0b11: 'Register Mode (no displacement)',
        }


def dis(stream, offset):
    byte1, byte2 = unpack_from('<BB', stream, offset)

    #print(f';{byte1=:02x} {byte1:08b}')
    #print(f';{byte2=:02x} {byte2:08b}')

    # opcode
    # |      direction
    # |      | width
    # |      | |
    # 000000 0 0    00 000 000
    #               |  |   |
    #               mod|   |
    #                  reg |
    #                      rm 

    opcode =    (byte1 >> 2) & 0b111111
    direction = (byte1 >> 1) & 0b1
    width =     (byte1 >> 0) & 0b1

    mod = (byte2 >> 6) & 0b111
    reg = (byte2 >> 3) & 0b111
    rm  = (byte2 >> 0) & 0b111

    #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')
    #print(f';{mod=:02b}, {reg=:03b}, {rm=:03b}')

    #print(mode_field_encoding[mod])

    if opcode == 0b100010: #mov
        if mod == 0b11:
            r1 = register_field_encoding[width][reg]
            r2 = register_field_encoding[width][rm]
            print(f'MOV {r2}, {r1}')
        elif mod == 0b10:
            assert False
        elif mod == 0b01:
            assert False
        else:
            assert False
    else:
        assert False

    return 2

def main(filepath):
    print(f'; {filepath}')
    print('bits 16')

    with open(filepath, 'rb') as f:
        data = f.read()
    #print(data)

    end = len(data)
    i = 0
    while i < end:
        length = dis(data, i)
        i += length

    assert i == end


if __name__ == '__main__':
    main(*argv[1:])
