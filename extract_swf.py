#!/usr/bin/env python3

# Author: Nathan Ostgard (noonat)
# Original Source: https://gist.github.com/noonat/821548
# Updated: 10 May 2020 for Python 3 by Corey Forman (https://github.com/digitalsleuth)
# Resulting output is a decompressed SWF file, extracted from the projector binary

import os.path
import struct
import sys
import zlib
from time import time

def open_file(filename):
    print("Reading: %s" % repr(filename))
    with open(filename, "rb") as f:
        buffer = f.read()
    parse_file(buffer)

def parse_file(buffer):
    current_time = int(time())
    for i in range(len(buffer) - 8):
        (id0, id1, id2, version, length) = struct.unpack_from("<BBBBI", buffer, i)
        if ((id0 != ord("F") and id0 != ord("C")) or id1 != ord("W") or
            id2 != ord("S") or version < 6 or version > 10 or length <= 0): 
            continue
        print("Found a valid header:")
        print("  ID: %c%c%c" % (id0, id1, id2))
        print("  Version: %i" % (version))
        print("  Length: %u" % (length))
        if id0 == ord("C"):
            swf = "F".encode('utf-8') + buffer[i + 1:]
            print("  Decompressing... ", end = '')
            try:
                swf = swf[0:8] + zlib.decompress(swf[8:])
                print("ok.")
            except zlib.error as e:
                print(e)
        else:
            swf = buffer[i:i + length]
        if len(swf) != length:
            print("  Error: wrong length (%d)" % len(swf))
        else:
            out_filename = "out%s.swf" % current_time
            with open(out_filename, "wb") as f:
                f.write(swf)
            print("  Wrote swf to %s" % (out_filename))

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)
if not sys.argv[1] or not os.path.isfile(sys.argv[1]):
    print("Error: Unable to read file %s" % repr(sys.argv[1]))
    sys.exit(2)
else:
    open_file(sys.argv[1])
