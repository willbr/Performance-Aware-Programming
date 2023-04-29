from rich.console import Console
from rich.traceback import install

from sys import argv
from struct import (
        unpack_from,
        )

#install(show_locals=True)

console = Console(markup=False)
python_print = print
print = console.print

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


effective_address_calculation = [
        [
            '[BX + SI]',
            '[BX + DI]',
            '[BP + SI]',
            '[BP + DI]',
            '[SI]',
            '[DI]',
            'DIRECT ADDRESS',
            '[BX]',
        ],
        [
            '[BX + SI + {d8}]',
            '[BX + DI + {d8}]',
            '[BP + SI + {d8}]',
            '[BP + DI + {d8}]',
            '[SI + {d8}]',
            '[DI + {d8}]',
            '[BP + {d8}]',
            '[BX + {d8}]',
        ],
        [
            '[BX + SI + {d16}]',
            '[BX + DI + {d16}]',
            '[BP + SI + {d16}]',
            '[BP + DI + {d16}]',
            '[SI + {d16}]',
            '[DI + {d16}]',
            '[BP + {d16}]',
            '[BX + {d16}]',
        ],
        ]


def dis(stream, offset):
    byte1, *_ = unpack_from('<B', stream, offset)

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


    #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')
    #print(f';{mod=:02b}, {reg=:03b}, {rm=:03b}')

    #print(mode_field_encoding[mod])

    if opcode == 0b100010: #mov
        byte2, *_ = unpack_from('<B', stream, offset + 1)
        mod = (byte2 >> 6) & 0b11
        reg = (byte2 >> 3) & 0b111
        rm  = (byte2 >> 0) & 0b111

        direction = (byte1 >> 1) & 0b1
        width =     (byte1 >> 0) & 0b1

        if mod == 0b11:
            r1 = register_field_encoding[width][reg]
            r2 = register_field_encoding[width][rm]
            print(f'MOV {r1}, {r2}' if direction else f'MOV {r2}, {r1}')
            return 2

        r1 = register_field_encoding[width][reg]
        s = effective_address_calculation[mod][rm]

        #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')
        #print(f';{mod=:02b}, {reg=:03b}, {rm=:03b}')

        if mod == 0b10:
            data, *_ = unpack_from('<h', stream, offset+2)
            s2 = s.format(d16=data).replace(' + 0]', ']')
            print(f'MOV {r1}, {s2}' if direction else f'MOV {s2}, {r1}')
            return 4
        elif mod == 0b01:
            data, *_ = unpack_from('<b', stream, offset+2)
            s2 = s.format(d8=data).replace(' + 0]', ']')
            print(f'MOV {r1}, {s2}' if direction else f'MOV {s2}, {r1}')
            return 3
        else:
            print(f'MOV {r1}, {s}' if direction else f'MOV {s}, {r1}')
            return 2

    elif (opcode >> 2) == 0b1011:
        width =   (byte1 >> 3) & 0b1
        reg = (byte1 >> 0) & 0b111
        #print(f'{width=} {reg=}')
        if width:
            data, *_ = unpack_from('<h', stream, offset+1)
            r1 = register_field_encoding[width][reg]
            print(f'MOV {r1}, {data}')
            return 3
        else:
            assert False
    else:
        print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')
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
