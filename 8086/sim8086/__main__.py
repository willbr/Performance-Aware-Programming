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
        [ 'al', 'cl', 'dl', 'bl', 'ah', 'ch', 'dh', 'bh'], #  8-bit
        [ 'ax', 'cx', 'dx', 'bx', 'sp', 'bp', 'si', 'di'], # 16-bit
        ]


mode_field_encoding = {
        0b00: 'Memory Mode, no displacement follows',
        0b01: 'Memory Mode, 8-bit displacement follows',
        0b10: 'Memory Mode, 16-bit displacement follows',
        0b11: 'Register Mode (no displacement)',
        }


effective_address_calculation = [
        [
            '[bx + si]',
            '[bx + di]',
            '[bp + si]',
            '[bp + di]',
            '[si]',
            '[di]',
            'DIRECT ADDRESS',
            '[bx]',
        ],
        [
            '[bx + si{rhs}]',
            '[bx + di{rhs}]',
            '[bp + si{rhs}]',
            '[bp + di{rhs}]',
            '[si{rhs}]',
            '[di{rhs}]',
            '[bp{rhs}]',
            '[bx{rhs}]',
        ],
        [
            '[bx + si{rhs}]',
            '[bx + di{rhs}]',
            '[bp + si{rhs}]',
            '[bp + di{rhs}]',
            '[si{rhs}]',
            '[di{rhs}]',
            '[bp{rhs}]',
            '[bx{rhs}]',
        ],
    ]


def dis(stream, initial_offset):
    offset = initial_offset

    def read_u8():
        nonlocal offset
        u8, *_ = unpack_from('<B', stream, offset)
        offset += 1
        return u8

    def read_i8():
        nonlocal offset
        i8, *_ = unpack_from('<b', stream, offset)
        offset += 1
        return i8

    def read_i16():
        nonlocal offset
        i16, *_ = unpack_from('<h', stream, offset)
        offset += 2
        return i16

    byte1 = read_u8()

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

    #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')

    def effective_address(n):
        if data > 0:
            rhs = f' + {data}'
        elif data == 0:
            rhs = ''
        else:
            rhs = f' {data}'
        s2 = s.format(rhs=rhs)
        return s2

    if opcode == 0b100010: # move register/memory to/from register
        byte2 = read_u8()
        mod = (byte2 >> 6) & 0b11
        reg = (byte2 >> 3) & 0b111
        rm  = (byte2 >> 0) & 0b111
        #print(f';{mod=:02b}, {reg=:03b}, {rm=:03b}')

        if mod == 0b11:
            r1 = register_field_encoding[width][reg]
            r2 = register_field_encoding[width][rm]
            print(f'mov {r1}, {r2}' if direction else f'mov {r2}, {r1}')
            return 2

        r1 = register_field_encoding[width][reg]
        s = effective_address_calculation[mod][rm]

        #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')
        #print(f';{mod=:02b}, {reg=:03b}, {rm=:03b}')

        if mod == 0b10:
            data = read_i16()
            s2 = effective_address(data)
            print(f'mov {r1}, {s2}' if direction else f'mov {s2}, {r1}')
            return 4
        elif mod == 0b01:
            data = read_i8()
            s2 = effective_address(data)
            print(f'mov {r1}, {s2}' if direction else f'mov {s2}, {r1}')
            return 3
        else:
            if rm == 0b110:
                data = read_i16()
                s2 = f'[{data}]'
            else:
                s2 = s

            print(f'mov {r1}, {s2}' if direction else f'mov {s2}, {r1}')
            length = offset - initial_offset
            return length

    elif opcode == 0b110001: # move immediate to register/memory
        width =   (byte1 >> 0) & 0b1

        byte2 = read_u8()

        mod = (byte2 >> 6) & 0b11
        reg = (byte2 >> 3) & 0b111
        rm  = (byte2 >> 0) & 0b111
        assert reg == 0

        s = effective_address_calculation[mod][rm]

        #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')
        #print(f'{s=}')

        if mod == 0b11:
            assert False
        elif mod == 0b10:
            data = read_i16()
            s2 = effective_address(data)
        elif mod == 0b01:
            data = read_u8()
            s2 = effective_address(data)
        else:
            assert rm != 0b110
            s2 = s

        if width:
            data = read_i16()
            i = f'word {data}'
        else:
            data = read_u8()
            i = f'byte {data}'

        dst, src =  (s2, i) if direction else (i, s2)

        print(f'mov {dst}, {src}')

        length = offset - initial_offset
        return length

    elif (opcode >> 2) == 0b1011: # move immediate to register
        width =   (byte1 >> 3) & 0b1
        reg = (byte1 >> 0) & 0b111
        #print(f'{width=} {reg=}')
        if width:
            data = read_i16()
            r1 = register_field_encoding[width][reg]
            print(f'mov {r1}, {data}')
            return 3
        else:
            data = read_u8()
            assert False

    elif opcode == 0b101000:
        data = read_i16()
        #print(f';{data=}')

        #print(f';{opcode=:06b}, {direction=:0b}, {width=:b}')

        s2 = 'ax'
        i = f'[{data}]'

        dst, src =  (i, s2) if direction else (s2, i)

        length = offset - initial_offset
        print(f'mov {dst}, {src}')
        return length
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
