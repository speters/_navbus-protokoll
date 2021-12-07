#!/usr/bin/env python

import argparse, pathlib

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

            for n in range(len(chunk)):
                # TODO: check which states may contain 0x71 and which require byte stuffing to 0x71 0x71
                prev_c = c
                c = chunk[n]
                print(hex(c) + " "+state)

                if (prev_c == 0x71):
                    if (c == 0x71):
                        stuffed != stuffed
                    if stuffed != True:
                        if (c == 0x00):
                            state = 'framestart'
                        if (c == 0x01):
                            state = 'frameend'

                if state == 'unknown':
                    subframe_len = 0
                    subframe_n = 0
                    subframe_type = 0
                    #prev_c = 0x01
                    stuffed = False

                    if c == 0x71:
                        state = 'framestart'
                    else:
                        state = 'unknown'
                elif state == 'framestart':
                    if c == 0x00:
                        state = 'subframelen'
                    else:
                        state = 'unknown'
                elif state == 'subframelen':
                    subframe_len = int(c)
                    if subframe_len < 2:
                        state = 'unknown'
                    else:
                        subframe_n = 1
                        state = 'subframetype'
                elif state == 'subframetype':
                    subframe_type = int(c)
                    subframe_n += 1
                    state = 'subframetstamp'
                elif state == 'subframetstamp':
                    subframe_n += 1
                    state = 'subframetstamp2'
                elif state == 'subframetstamp2':
                    subframe_n += 1
                    state = 'subframedata'
                elif state == 'subframedata':
                    if (subframe_n +3) < subframe_len:
                        subframe_n += 1
                    else:
                        state = 'subframecrc'
                elif state == 'subframecrc':
                    state = 'subframecrc2'
                elif state == 'subframecrc2':
                    state = 'frameendlead'
                elif state == 'frameendlead':
                    if c == 0x71:
                        state = 'frameend'
                    else:
                        state = 'unknown'
                elif state == 'frameend':
                    if c == 0x00:
                        # frame complete
                        pass
                    state = 'unknown'
                else:
                    state = 'unknown'






