#!/usr/bin/python3
import sys
import numpy.linalg as np


def solve(input):
    f = open(input, 'r', encoding='utf8')
    dict = {}
    for line in f:
        operand = None
        for one in line.split(" "):
            if one == '+' or one == '-' or one == '=':
                operand = one
            else:
                if operand != '=':
                    number = one[:-1]
                    if number is None:
                        number = 1
                    elif number == '':
                        number = 1
                    else:
                        number = int(number)
                    coeficient = one[-1:]
                    if coeficient not in dict:
                        dict[coeficient] = []
                    if operand == '-':
                        dict[coeficient].append(int(operand + str(number)))
                        print(operand + one)
                    else:
                        dict[coeficient].append(number)
                        print(one)
                else:
                    if 'result' not in dict:
                        dict['result'] = []
                    dict['result'].append(int(one))
    print(dict)

        # iterator = iter(line.split(" "))
        # item = next(iterator, None)
        # while item is not None:
        #     print(item)
        #
        #     item = next(iterator, None)
        # print(line)
    print()

if __name__ == "__main__":

    if len(sys.argv) == 2:
        solve(sys.argv[1])
    else:
        print("Wrong number of arguments")