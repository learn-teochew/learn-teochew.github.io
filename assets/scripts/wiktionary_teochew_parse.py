#!/usr/bin/env python3

# from xml.etree import ElementTree as ET
import pengim_utils as pu
import bz2
import re
from collections import defaultdict
import json
import argparse

parser = argparse.ArgumentParser(description="Extract Teochew pronunciations from En Wiktionary")
parser.add_argument('--dump', type=str, action='store', help="Article data dump from English Wiktionary")
parser.add_argument('--scraped', type=str, action='store', help="JSON file already produced by scraping the data dump. If supplied, then argument to --dump is ignored")
parser.add_argument('--out', type=str, default='teochew_scrape.json', help="Path to write scraped data, keyed by character")
parser.add_argument('--out_pron_prefix', type=str, default='teochew_scrape_pron_', help="Prefix to write markdown files, sorted by head letter and pronunciation")
parser.add_argument('--out_pron_suffix', type=str, default='md', help="Suffix for markdown files.")
parser.add_argument('--limit', type=int, default=-1, help="Stop after the first N entries in the input")

args = parser.parse_args()

if (args.scraped):
    # If JSON file of scraped data already produced (do not process Wiktionary dump file)
    fh_j = open(args.scraped,"r")
    outdict = json.load(fh_j)
    fh_j.close()
else:
    # Process de novo from Wiktionary dump file
    outdict = pu.parse_wiktionary_dump(args)
    fh_w = open(args.out,"w")
    json.dump(outdict,fh_w)
    fh_w.close()

pron_dict = defaultdict(lambda: defaultdict(list))
for key in outdict.keys():
    for tprons in outdict[key]['mn-t']:
        for tpron in re.split("\s*/\s*",tprons): # Split on slash if alternative pronunciations given
            headletter = ''
            # Sort by first letter, but check first for bh, gh, and ng digraphs
            if tpron.startswith('gh'):
                headletter = 'gh'
            elif tpron.startswith('bh'):
                headletter = 'bh'
            elif tpron.startswith('ng'):
                headletter = 'ng'
            else: # Otherwise just take the first letter
                try:
                    headletter = tpron[0]
                except:
                    headletter = "NA"
            pron_dict[headletter][tpron].append((key, tprons))

for key in sorted(pron_dict):
    fh_p = open(args.out_pron_prefix+key+"."+args.out_pron_suffix,"w")
    fh_p.write("# "+key+"\n\n")
    fh_p.write("--------|---------------|-----------|------------------------------|--------------------------\n")
    fh_p.write("Peng'im | Flattened IPA | Character | All pronunciations (Peng'im) | All pronunciations (FIPA)\n")
    fh_p.write("--------|---------------|-----------|------------------------------|--------------------------\n")
    for pron in sorted(pron_dict[key]):
        fipa = pu.convert_pengim_tonemarks(pu.convert_pengim2fipa(pron))
        fh_p.write(pron + " | " + fipa + " | | |\n")
        for (char, pronall) in pron_dict[key][pron]:
            fipaall = pu.convert_pengim_tonemarks(pu.convert_pengim2fipa(pronall))
            fh_p.write("| | ["+char+"](https://en.wiktionary.org/wiki/"+char+") | " + pronall+" | " + fipaall + "\n")
    fh_p.write("--------|---------------|-----------|------------------------------|--------------------------\n")
    fh_p.close()
