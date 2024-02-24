#!/usr/bin/env python3

import json
import argparse
import sys


def rubify(char, annot):
    """Return ruby annotated html tag

    Multiple pronunciations are stacked with breaklines
    within the ruby text
    """
    return f"<ruby>{char}<rt>{annot}</rt></ruby>"


# CJK punctuation to Western
puncdict = {
    "，": ",",
    "。": ".",
    "、": ",",
    "！": "!",
    "？": "?",
    "；": ";",
    "：": ":",
    "「": "‘",
    "」": "’",
    "【": "[",
    "】": "]",
    "（": "(",
    "）": ")",
    "《": "“",
    "》": "”",
}

parser = argparse.ArgumentParser(
    description="Convert chinese characters to peng'im with dictionary"
)
parser.add_argument(
    "-i",
    "--input",
    type=argparse.FileType("r"),
    nargs="?",
    default=sys.stdin,
    action="store",
    help="""
    File with chinese characters to be converted to peng'im, read from STDIN
    otherwise
    """,
)
parser.add_argument(
    "-d",
    "--dict",
    type=str,
    action="store",
    help="""
    JSON file with dictionary, produced by scraping Wiktionary dump with
    wiktionary_teochew_parse.py
    """,
)
parser.add_argument(
    "-f",
    "--format",
    default="html",
    help="""
    Output format: 'html' - html with pengim as ruby, 'replace' - replace hanzi
    with pengim, 'interlinear' - original lines interleaved with pengim
    """,
)
args = parser.parse_args()

# Read dictionary
dd_fh = open(args.dict, "r")
dd = json.load(dd_fh)
dd_fh.close()

# Process input

# Output html
if args.format == "html":
    print("<!DOCTYPE html>\n<html>\n<body>")
    for line in args.input:
        outline = []
        for i in line.rstrip():
            if i in [str(i) for i in range(10)]:
                outline.append(i)
            elif i in dd and "mn-t" in dd[i]:
                # flatten multiple pronunciations into a single list
                prons = [rec.split("/") for rec in dd[i]["mn-t"]]
                prons = [item for sublist in prons for item in sublist]
                prons = sorted(set(prons))
                outline.append(rubify(i, "<br/>".join(prons)))
            else:
                outline.append(i)
        print("<p>" + "".join(outline) + "</p>")
    print("</body></html>")

# output replace text with peng'im
elif args.format == "replace":
    for line in args.input:
        outline = []
        line = line.rstrip()
        for i in line:
            if i in [str(i) for i in range(10)]:
                outline.append(i)
            elif i in dd and "mn-t" in dd[i]:
                outline.append("/".join(dd[i]["mn-t"]))
            else:
                outline.append(i)
        print("".join(outline))
        print("\n")

# Output interleave original text with peng'im
else:
    for line in args.input:
        outline = []
        for i in line.rstrip():
            if i in [str(i) for i in range(10)]:
                # Avoid numerals
                outline.append(i)
            elif i in dd and "mn-t" in dd[i]:
                # characters with Pengim, if multiple join with /
                outline.append("/".join(dd[i]["mn-t"]) + " ")
            elif i in puncdict:
                # CJK punctuation to western
                outline.append(puncdict[i] + " ")
            else:
                # outline.append("X")
                outline.append(i)
        if line.rstrip() == "".join(outline):
            print(line.rstrip())
            print("---")
        else:
            print(line.rstrip())
            print("".join(outline))
            print("---")
