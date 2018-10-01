#!/usr/bin/python3
import sys
import scorelib

def print_out(file):
    list = scorelib.load(file)
    for item in list:
        item.format()

if __name__ == "__main__":

    if len(sys.argv) == 2:
        print_out(sys.argv[1])
    else:
        print("Wrong number of arguments")