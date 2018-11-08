#!/usr/bin/python3
import sys
import numpy as np
import re


def solve(input):
    f = open(input, 'r', encoding='utf8')
    dict = {}
    results = []
    for line in f:
        number = 1
        for match in re.finditer(r"([+\-=])\s+(\d*)([a-z]*)|(\d*)([a-z])", line):
            if match.group(1) is None:
                if match.group(5) is not None:
                    if match.group(5) not in dict:
                        dict[match.group(5)] = []
                        for i in range(0, len(results)):
                            dict[match.group(5)].append(0)
                    if match.group(4) is None:
                        number = 1
                    else:
                        if match.group(4) == '':
                            number = 1
                        else:
                            number = int(match.group(4))
                    dict[match.group(5)].append(number)
            else:
                if match.group(1) == '+' or match.group(1) == '-':
                    if match.group(3) not in dict:
                        dict[match.group(3)] = []
                        for i in range(0, len(results)):
                            dict[match.group(3)].append(0)
                    if match.group(2) is None:
                        number = int(match.group(1) + '' + '1')
                    else:
                        if match.group(2) == '':
                            number = int(match.group(1) + '' + '1')
                        else:
                            number = int(match.group(1) + '' + match.group(2))
                    dict[match.group(3)].append(number)
                else:
                    results.append(int(match.group(2)))
        for (key, value) in dict.items():
            if len(value) < len(results):
                value.append(0)

    # print(dict)
    # print(results)

    a = np.empty((0, len(results)))
    for key in sorted(dict):
        a = np.append(a, [np.array(dict[key])], axis=0)
    b = np.array(results)
    a = a.T
    # c = np.concatenate((a, b[:, None]), axis=1)
    # print(c)
    rank1 = np.linalg.matrix_rank(a)
    rank2 = np.linalg.matrix_rank(np.concatenate((a, b[:, None]), axis=1))
    if rank1 != rank2:
        print('no solution')
    else:
        if rank1 < (len(dict.keys())):
            dimension = len(dict.keys())-rank1
            print('solution space dimension:', dimension)
        else:
            # res = np.linalg.det(a)
            # print(res)
            x = np.linalg.solve(a,b)
            print('solution: ', end='')
            index = 0
            for key in sorted(dict):
                print(key, '=', x[index], end='', flush=True)
                if index < len(dict.keys()) - 1:
                    print(end=', ')
                index += 1
            print()

        # iterator = iter(line.split(" "))
        # item = next(iterator, None)
        # while item is not None:
        #     print(item)
        #
        #     item = next(iterator, None)
        # print(line)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        solve(sys.argv[1])
    else:
        print("Wrong number of arguments")