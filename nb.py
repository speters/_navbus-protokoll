#!/usr/bin/env python

import argparse, pathlib

# width=16 poly=0x1021 init=0xffff refin=true refout=true xorout=0x0000 check=0x6f91 residue=0x0000 name="CRC-16/MCRF4XX"
from crccheck.crc import Crc16Mcrf4Xx

parser = argparse.ArgumentParser()
parser.add_argument('filename', type=pathlib.Path, nargs='+') #type=argparse.FileType('r'))
args = parser.parse_args()

frame_end = b'\x71\x01'

for filename in args.filename:
    with open(filename, 'rb') as logf:
        chunks = logf.read().split(frame_end)
        for chunk in chunks:
            if len(chunk)<1:
                break
            else:
                # re-attach the frame ending
                chunk += frame_end
            print(" ".join('{:02X}'.format(n)  for n in chunk))

            state = 'unknown'
            subframe_len = 0
            subframe_n = 0
            subframe_type = 0
            c = 0x01
            stuffed = False
            inframe = False
            crcinst = Crc16Mcrf4Xx()

            for n in range(len(chunk)):
                # TODO: check which states may contain 0x71 and which require byte stuffing to 0x71 0x71
                prev_c = c
                c = chunk[n]

                if inframe == False:
                    if c == 0x00 and prev_c == 0x71:
                        inframe = True
                        stuffed = False
                        state = 'framestart'
                else:
                    if c == 0x71:
                        if stuffed:
                            prev_c = 0xff
                            stuffed = False
                        else:
                            stuffed = True
                            continue
                    elif stuffed:
                        stuffed = False
                        inframe = False
                        state = 'unknown'
                        if c == 0x01:
                            # frame end
                            state = 'frameend'
                        if c == 0x00:
                            # frame start, should not happen here
                            pass
#                print(hex(c) + " "+str(inframe)+str(stuffed))

                oldstate = state
                if state == 'framestart':
                    state = 'subframelen'
                elif state == 'subframelen':
                    subframe_len = int(c)
                    crcinst.process([c])
                    subframe_n = 0
                    subframe_type = 0
                    if subframe_len < 2:
                        state = 'unknown'
                    else:
                        subframe_n = 1
                        state = 'subframetype'
                elif state == 'subframetype':
                    subframe_type = int(c)
                    crcinst.process([c])
                    subframe_n += 1
                    state = 'subframetstamp'
                elif state == 'subframetstamp':
                    crcinst.process([c])
                    subframe_n += 1
                    state = 'subframetstamp2'
                elif state == 'subframetstamp2':
                    crcinst.process([c])
                    subframe_n += 1
                    state = 'subframedata'
                elif state == 'subframedata':
                    crcinst.process([c])
                    if (subframe_n +3) < subframe_len:
                        subframe_n += 1
                    else:
                        state = 'subframecrc'
                elif state == 'subframecrc':
                    crcinst.process([c])
                    subframe_n += 1
                    state = 'subframecrc2'
                elif state == 'subframecrc2':
                    crcinst.process([c])
                    if crcinst.final() != 0:
                        print("CRC error")
                        exit(1)
                    else:
                        crcinst.reset()
                    subframe_n += 1
                    state = 'subframelen'
                elif state == 'frameendlead':
                    if c == 0x71:
                        state = 'frameend'
                    else:
                        state = 'unknown'
                elif state == 'frameend':
                    if c == 0x01:
                        # frame complete
                        pass
                    state = 'unknown'
                    inframe = False
                else:
                    state = 'unknown'

                print(hex(subframe_n) + " "+ hex(c) + " "+oldstate)




