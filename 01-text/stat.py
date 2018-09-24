#!/usr/bin/python3

import sys
import re
from collections import Counter


def get_ordinal_number_ending(number):
    last_digit = re.search(r"\d{1}$", number).group(0)
    if (last_digit == '1'):
        return "st"
    elif (last_digit == '2'):
        return "nd"
    elif (last_digit == '3'):
        return "rd"
    else:
        return "th"


def get_century_from_year(year):
    if (int(year) % 100 == 0):
        century_year = int(year) // 100
    else:
        century_year = (int(year) // 100) + 1
    return str(century_year)


def print_collection(counter):
    for item in counter.most_common():
        print(str(item[0]) + ": "  + str(item[1]))


def composer(file):
    counter = Counter()
    f = open(file, 'r', encoding='utf8')
    for line in f:
        r = re.compile(r"Composer: (.*)")
        m = r.match(line)
        if m is None:
            continue
        else:
            splitted = m.group(1).split(";")
            for artist in splitted:
                no_brackets = re.sub(r"\(.*?\)", '', artist)
                no_spaces = re.sub(r"\s*$", '', no_brackets)
                no_spaces = re.sub(r"^\s*", '', no_spaces)
                if(no_spaces != ''):
                    counter[no_spaces] += 1
    print_collection(counter)


def century(file):
    counter = Counter()
    f = open(file, 'r', encoding='utf8')
    for line in f:
        r = re.compile(r"Composition Year: (.*)")
        m = r.match(line)
        if m is None:
            continue
        else:
            year = re.search(r"\d{3,4}", m.group(1))
            century_ordinal = re.search(r"\d{1,2}(?:st|nd|rd|th)", m.group(1))
            if year is not None:
                if year is not None:
                    year_century = get_century_from_year(year.group(0))
                    counter[year_century + get_ordinal_number_ending(year_century) + " century"] += 1
            elif century_ordinal is not None:
                counter[century_ordinal.group(0) + " century"] += 1
    print_collection(counter)

if __name__ == "__main__":

    if len(sys.argv) == 3:
        if (sys.argv[2] == "composer"):
            composer(sys.argv[1])
        if (sys.argv[2] == "century"):
            century(sys.argv[1])
    else:
        print("Wrong number of arguments")