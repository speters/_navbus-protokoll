#!/usr/bin/env python

import argparse, pathlib

parser = argparse.ArgumentParser()
parser.add_argument('filename', type=pathlib.Path, nargs='+') #type=argparse.FileType('r'))
args = parser.parse_args()

for filename in args.filename:
    with open(filename, 'rb') as logf:
        chunks = logf.read().split(b'\x71\x01')
        for chunk in chunks:
            print(" ".join('{:02X}'.format(n)  for n in chunk))

