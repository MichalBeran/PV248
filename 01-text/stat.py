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
            split = m.group(1).split(";")
            for artist in split:
                counter[re.sub( r"\s*", '', artist )] += 1
    for composer in counter:
        print(composer + " - "  + str(counter[composer]))

def century(file):
    f = open(file, 'r', encoding='utf8')
    for line in f:
        print(line)

if __name__ == "__main__":

    if len(sys.argv) == 3:
        if (sys.argv[2] == "composer"):
            composer(sys.argv[1])
        if (sys.argv[2] == "century"):
            century(sys.argv[1])
    else:
        print("Wrong args")