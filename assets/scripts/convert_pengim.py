#!/usr/bin/env python3

import pengim_utils as pu
import argparse
import sys

parser = argparse.ArgumentParser(
    description="Convert between Guangdong Peng'im and flattened IPA"
)
parser.add_argument(
    "-i",
    "--input",
    type=argparse.FileType("r"),
    nargs="?",
    default=sys.stdin,
    action="store",
    help="File with text to be converted",
)
parser.add_argument(
    "-o",
    "--output",
    type=argparse.FileType("w"),
    nargs="?",
    default=sys.stdout,
    action="store",
    help="File to write output",
)
parser.add_argument(
    "--input_format",
    action="store",
    type=str,
    default="pengim",
    help="Input format, either pengim or fipa",
)
parser.add_argument(
    "--output_format",
    action="store",
    type=str,
    default="fipa",
    help="Output format, either pengim, fipa, or ipa",
)
parser.add_argument(
    "-t",
    "--tone_marks",
    action="store_true",
    help="Convert tone numbers to tone marks?",
)

args = parser.parse_args()

# fh_in = open(args.input, 'r')
if args.input_format.startswith("p"):
    if args.output_format.startswith("f"):
        for line in args.input:
            if args.tone_marks:
                args.output.write(
                    pu.convert_pengim_tonemarks(pu.convert_pengim2fipa(line)) + "\n"
                )
            else:
                args.output.write(pu.convert_pengim2fipa(line) + "\n")
    elif args.output_format.startswith("i"):
        for line in args.input:
            args.output.write(pu.convert_pengim2ipa(line) + "\n")
    else:
        print("Please specify valid input and output formats")
elif args.input_format.startswith("f"):
    if args.output_format.startswith("p"):
        for line in args.input:
            if args.tone_marks:
                args.output.write(
                    pu.convert_pengim_tonemarks(pu.convert_fipa2pengim(line)) + "\n"
                )
            else:
                args.output.write(pu.convert_fipa2pengim(line) + "\n")
    elif args.output_format.startswith("i"):
        print("This output format not available for fipa-formatted input")
    else:
        print("Please specify valid input and output formats")
else:
    print("Please specify valid input and output formats")
