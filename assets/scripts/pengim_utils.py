#!/usr/bin/env python3

from collections import OrderedDict
from xml.etree import ElementTree as ET
from collections import defaultdict
import re
import bz2

def convert_fipa2pengim(text):
    fipa2pengim = OrderedDict ([('b', 'bh'), # Order of substitution is important
                            ('p', 'b'),
                            ('ph', 'p'),
                            ('z', 'r'),
                            (r't([^hs])', r'd\1'),
                            ('tsh', 'c'),
                            ('ts', 'z'),
                            ('th', 't'),
                            (r'([^n])g', r'\1gh'), # Except ng
                            (r'k([^h])', r'g\1'),
                            ('kh','k'),
                            (r'’([\d\s\n])', r'h\1'),
                            # vowels
                            ('au', 'ao'),
                            (r'e([^u])', r'ê\1'),
                            ('eu', 'e'),
                            # nasalized
                            (r'ih([\d\s\n])', r'in\1'),
                            (r'uh([\d\s\n])', r'un\1'),
                            (r'ar([\d\s\n])', r'an\1'),
                            (r'or([\d\s\n])', r'on\1'),
                           ])
    tochange = text
    for key in fipa2pengim:
        tochange = re.sub(key, fipa2pengim[key], tochange)
    return(tochange.rstrip())

def convert_pengim2fipa(text):
    pengim2fipa = OrderedDict ([('p', 'ph'), # Order is important
                            (r'b$', r'p'), # Edge case of final b at EOL
                            (r'b([^h])', r'p\1'),
                            ('bh', 'b'),
                            ('t', 'th'),
                            ('d', 't'),
                            ('z', 'ts'),
                            ('c', 'tsh'),
                            (r'k([^\d\s])', r'kh\1'),
                            (r'([^n])g([^h])', r'\1k\2'), # Avoid changing 'ng'
                            (r'^g([^h])', r'k\1'), # Edge case of initial g
                            ('gh', 'g'),
                            (r'h([\d\s\n])', r'’\1'), # Final stop 'h'
                            (r'h$', r'’'), # Edge case of final h at EOL
                            ('r', 'z'),
                            # vowels
                            ('ao', 'au'),
                            ('e', 'eu'),
                            ('ê', 'e'),
                            # nasalized
                            (r'in([\d\s\n])', r'ih\1'),
                            (r'un([\d\s\n])', r'uh\1'),
                            (r'en([\d\s\n])', r'er\1'),
                            (r'an([\d\s\n])', r'ar\1'),
                            (r'on([\d\s\n])', r'or\1'),
                           ])
    tochange=text
    for key in pengim2fipa:
        tochange = re.sub(key, pengim2fipa[key], tochange)
    return(tochange.rstrip())

def convert_pengim2ipa(text):
    # Convert Peng'im to IPA - assumes that input has tone numbers on ALL syllables
    pengim2ipa = OrderedDict([('p', 'pʰ'),
                              (r'b$', 'p'),
                              (r'b([^ʰ])', r'p\1'),
                              ('bh', 'b'),
                              ('t', 'tʰ'),
                              ('d', 't'),
                              ('z', 'ts'),
                              ('c', 'tsʰ'),
                              (r'k([^\d\s])', r'kʰ\1'),
                              ('ng', 'ŋ'),
                              (r'g([^h])', r'k\1'),
                              ('gh', 'g'),
                              (r'h([\d\s\n])', r'ʔ\1'),
                              ('r', 'z'),
                              # vowels
                              ('ao', 'au'),
                              ('e', 'ɯ'),
                              ('ê', 'e')
                             ])
    tochange = text.lower()
    for key in pengim2ipa:
        tochange = re.sub(key, pengim2ipa[key], tochange)
    # Nasalized vowels TK
    textsplit = re.split(r'([\wʰŋɯ]+?\d)',tochange)
    # Translation tables for nasalized vowels
    # Cannot use str.maketrans because vowel + nasal mark are two chars
    # trn = str.maketrans('aeiouɯ','ãẽĩõũɯ̃')
    trn = {'a':'ã',
           'e':'ẽ',
           'i':'ĩ',
           'o':'õ',
           'u':'ũ',
           'ɯ':'ɯ̃'}

    # Translation dict for tone marks:
    trt = {'1':'˧',
           '2':'˥˧',
           '3':'˨˩˧',
           '4':'˨.',
           '5':'˥',
           '6':'˧˥',
           '7':'˩',
           '8':'˥.'}
    out = []
    for i in textsplit:
        im = re.match(r'([^n]+)n(\d)',i)
        if (im): # Contains a nasalized vowel
            # out.extend(im.group(1).translate(trn)) # nasalize vowels, omit the final 'n' char
            for char in im.group(1):
                if char in trn.keys():
                    # If matching a vowel, nasalize it
                    out.extend(trn[char])
                else:
                    out.extend(char)
            out.extend(trt[im.group(2)]) # tone mark
        else:
            for char in i:
                if char in trt.keys(): # tone mark
                    out.extend(trt[char])
                else:
                    out.extend(char)
    # return(tochange.rstrip())
    return(''.join(out))

def convert_pengim_tonemarks(text):
    # Split text into tone-numbered chunks
    # If no tones given this will just default to adding no marks
    # Use grouping parens () in regex to retain matches and non-matches
    textsplit = re.split(r'([’\w]+?\d)',text) # use ? for minimal match, e.g. for hak4hau6
    # Translate tables for unaccented to accented, for each tone
    # Unfortunately handling has to be different because not all letters have all tone marks available
    tr2 = str.maketrans('AEIOUMNaeioumn','ÀÈÌÒÙMǸàèìòùmǹ') # Syllable either has vowel, or is m or ng
    tr37 = str.maketrans('AEIOUMNaeioumn','ǍĚǏǑǓMŇǎěǐǒǔmň')
    tr58 = str.maketrans('AEIOUMNaeioumn','ĀĒĪŌŪMNāēīōūmn')
    tr6 = str.maketrans('AEIOUMNaeioumn','ÁÉÍÓÚḾŃáéíóúḿń')
    out = []
    for i in textsplit:
        im = re.match(r'([’\w]+?)(\d)',i)
        if (im):
            if (int(im.group(2)) == 2):
                if (im.group(1).lower() == 'm'): # Edge case: m2 (no `m symbol available)
                    out.extend(i)
                elif (im.group(1).lower() == 'ng'): # avoid situation like ňga
                    out.extend(re.sub(r'[Nn]', lambda x: x.group().translate(tr2), im.group(1), count=1))
                else:
                    # Replace only the first instance of a vowel
                    out.extend(re.sub(r'[AEIOUaeiou]', lambda x: x.group().translate(tr2), im.group(1), count=1))
            elif(int(im.group(2)) == 3 or int(im.group(2)) == 7):
                if (im.group(1).lower() == 'm'): # Edge case: m3 or m7, no ˇm symbol available
                    out.extend(i)
                elif (im.group(1).lower() == 'ng'): # avoid situation like ňga
                    out.extend(re.sub(r'[Nn]', lambda x: x.group().translate(tr37), im.group(1), count=1))
                else:
                    out.extend(re.sub(r'[AEIOUaeiou]', lambda x: x.group().translate(tr37), im.group(1), count=1))
            elif(int(im.group(2)) == 5 or int(im.group(2)) == 8):
                if (im.group(1).lower() == 'm' or im.group(1).lower() == 'ng'): # Edge cases m5 and ng5
                    out.extend(i)
                else:
                    out.extend(re.sub(r'[AEIOUaeiou]', lambda x: x.group().translate(tr58), im.group(1), count=1))
            elif(int(im.group(2)) == 6):
                if (im.group(1).lower() == 'm'):
                    out.extend(i)
                elif(im.group(1).lower() == 'ng'):
                    out.extend(re.sub(r'[Nn]', lambda x: x.group().translate(tr6), im.group(1), count=1))
                else:
                    out.extend(re.sub(r'[AEIOUaeiou]', lambda x: x.group().translate(tr6), im.group(1), count=1))
            else:
                out.extend(im.group(1))
        else:
            out.extend(i)
    # Return string joined together again
    return(''.join(out))

def parse_wiktionary_dump(args):
# Parse wiktionary dump file and report Teochew pronunciations to dict
    # Counter for pages
    counter = 0 
    # Dict to store results, keyed by page title
    outdict = defaultdict(lambda: defaultdict(dict))
    # Name of Wiktionary dump file
    # fh = bz2.BZ2File("enwiktionary-20200220-pages-articles.xml.bz2")
    fh = bz2.BZ2File(args.dump)
    # Holder for current title
    currtitle = ""
    # Holder for namespace
    namespace = ""
    # Iterate through Wiktionary file
    for (event, elem) in ET.iterparse(fh,events=('start','end')):
        # Get namespace prefix from root mediawiki element
        # Need to add namespace to element tags later on
        if (event == 'start' and elem.tag.endswith('mediawiki')):
            namespace = re.match("(\{.+\})mediawiki", elem.tag).group(1)
        if (event == 'end' and elem.tag == namespace + 'page'): # Use endswith because tags have a file-specific prefix
            counter += 1 # Count each page = each entry
            if (counter % 50000 == 0):
                print ("Processed " + str(counter) + "pages")
            if (args.limit > 0 and counter >= args.limit): # Break out of loop - for previewing
                elem.clear()
                break
            # Get current page title
            currtitle = elem.find(namespace + 'title').text
            # Skip pages that are not articles
            if (not currtitle.startswith('MediaWiki') and not currtitle.startswith('Wiktionary') and not currtitle.startswith('Template') and not currtitle.startswith('Module')):
                # Get page text, nested in revision element
                pagerevision = elem.find(namespace + 'revision')
                pagetext = pagerevision.find(namespace + 'text').text
                # Search text for teochew pronunciation in zh-pron template
                # Assumes that editors do not deviate from template
                try:
                    matches_t = re.findall("\|mn-t=([^\|\n]+)",pagetext)
                except TypeError:
                    print ("TypeError at entry " + currtitle)
                if (matches_t):
                    # If there is a match, also look for pronunciation notes
                    # and Mandarin pronunciation
                    matches_t_notes = re.findall("\|mn-t_note=([^\|\n]+)",pagetext)
                    matches_m = re.findall("\|m=([^\|\n]+)",pagetext)
                    outdict[currtitle]['mn-t'] = matches_t
                    if (matches_t_notes):
                        outdict[currtitle]['mn-t_note'] = matches_t_notes
                    if (matches_m):
                        outdict[currtitle]['m'] = matches_m
            # Clear page element from memory after processing
            elem.clear()
    return(outdict)
