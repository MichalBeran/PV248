#!/usr/bin/python3

import sys
import re
from collections import Counter

def composer(file):
    counter = Counter()
    f = open(file, 'r', encoding='utf8')
    for line in f:
        r = re.compile(r"Composer: (.*)")
        m = r.match(line)
        if m is None:
            continue
        else:
            no_brackets = re.sub( r"\(.*?\)", '', m.group(1))
            splited = no_brackets.split(";")
            for artist in splited:
                no_spaces = re.sub(r"\s*$", '', artist)
                no_spaces = re.sub(r"^\s*", '', no_spaces)
                if(no_spaces != ''):
                    counter[no_spaces] += 1
    for composer in counter.most_common():
        print(str(composer[0]) + " - "  + str(composer[1]))

def century(file):
    counter = Counter()
    f = open(file, 'r', encoding='utf8')
    for line in f:
        r = re.compile(r"Composition Year: (.*)")
        m = r.match(line)
        if m is None:
            continue
        else:
            # 17th century (?<=[0-9])(?:st|nd|rd|th)  \d{1,2}(?:st|nd|rd|th)
            # 1956 \d{4}
            # 15.1.1960
            # ca 1870
            # 1732 Paris
            year = re.search(r"\d{4}", m.group(1))
            century_ordinal = re.search(r"\d{1,2}(?:st|nd|rd|th)", m.group(1))
            # print(m.group(1))
            if year is not None:
                year = re.match(r"(\d{1,2})(\d{2})", year.group(0))
                if year is not None:
                    year_century = year.group(1)
                    if year.group(2) != "00":
                        year_century = str(int(year_century) + 1)
                counter[year_century + "th century"] += 1
                # print(">>" + year_century)
            if century_ordinal is not None:
                # century_ordinal = re.match(r"\d{1,2}", century_ordinal.group(0))
                counter[century_ordinal.group(0) + " century"] += 1
                # print(">>" + century_ordinal.group(0))

    for cent in counter.most_common():
        print(str(cent[0]) + " - "  + str(cent[1]))

if __name__ == "__main__":

    if len(sys.argv) == 3:
        if (sys.argv[2] == "composer"):
            composer(sys.argv[1])
        if (sys.argv[2] == "century"):
            century(sys.argv[1])
    else:
        print("Wrong args")