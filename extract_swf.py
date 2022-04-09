#!/usr/bin/env python3

'''
# Author: Nathan Ostgard (noonat)
# Original Source: https://gist.github.com/noonat/821548
# Updated: 10 May 2020 for Python 3 by Corey Forman (https://github.com/digitalsleuth)
# Updated: 9 Apr 2022 - Modified output to include offset and an index value
# Resulting output is a decompressed SWF file, extracted from the provided binary
# TODO: Convert output to csv format
'''

import argparse
import os.path
import struct
import sys
import zlib

__original_author__ = 'Nathan Ostgard (noonat)'
__current_author__ = 'Corey Forman (digitalsleuth)'
__version__ = '2.0.0'
__description__ = 'Python 3 script to extract SWF files from binaries'


def open_file(filename):
    """
    Opens file as a binary file and reads into buffer then
    passes the buffer to parse_file
    """
    print(f"Reading: {repr(filename)}")
    with open(filename, "rb") as input_file:
        buffer = input_file.read()
    parse_file(buffer, filename)


def parse_file(buffer, filename):
    """
    Reads buffer, unpacks to find CWS or SWF magic
    Prints details, then extracts and decompresses SWF file
    """
    index = 0
    for i in range(len(buffer) - 8):
        offset = hex(i)
        (id0, id1, id2, version, length) = struct.unpack_from("<BBBBI", buffer, i)
        if ((id0 != ord("F") and id0 != ord("C")) or id1 != ord("W") or
                id2 != ord("S") or version < 6 or version > 12 or length <= 0):
            continue
        print("Found a valid header:")
        print(f"  Offset: {offset}")
        print(f"  ID: {id0}{id1}{id2}")
        print(f"  Version: {version}")
        print(f"  Length: {length}")
        if id0 == ord("C"):
            swf = "F".encode('utf-8') + buffer[i + 1:]
            print("  Decompressing... ", end='')
            try:
                swf = swf[0:8] + zlib.decompress(swf[8:])
                print("OK")
            except zlib.error as err:
                print(err)
        else:
            swf = buffer[i:i + length]
        if len(swf) != length:
            print(f"  Error: wrong length {len(swf)}")
        else:
            out_filename = "%s-%s-%s.swf" % (filename, index, offset)
            with open(out_filename, "wb") as output_file:
                output_file.write(swf)
            print(f"  Wrote swf to {out_filename}")
            index += 1


def main():
    """
    Parse arguments, pass to open_file
    """
    arg_parse = argparse.ArgumentParser(description=__description__ + ' - extract_swf.py v' +
                                        str(__version__))
    arg_parse.add_argument('--version', '-v', action='version', version='%(prog)s ' +
                           str(__version__))
#    arg_parse.add_argument('--csv', 'c', action='store_true', help='print output as csv')
    arg_parse.add_argument('file', metavar='file')

    if len(sys.argv[1:]) == 0:
        arg_parse.print_help()
        arg_parse.exit()

    args = arg_parse.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: Unable to read file {repr(args.file)}! Does it exist?")
        sys.exit(2)
    else:
        open_file(args.file)


if __name__ == '__main__':
    main()
