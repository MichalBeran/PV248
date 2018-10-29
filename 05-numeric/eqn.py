#!/usr/bin/python3
import sys
import numpy as np


def solve(input):
    f = open(input, 'r', encoding='utf8')
    dict = {}
    results = []
    line_number = 0
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
                        for i in range(0, line_number):
                            dict[coeficient].append(0)
                    if operand == '-':
                        dict[coeficient].append(int(operand + str(number)))
                    else:
                        dict[coeficient].append(number)
                else:
                    results.append(int(one))
        line_number += 1
        for (key, value) in dict.items():
            if len(value) < line_number:
                value.append(0)
    # print(dict)

    a = np.empty((0, line_number))
    for (key, value) in dict.items():
        a = np.append(a, [np.array(value)], axis=0)
    b = np.array(results)

    # print(a)
    # print(a.T)
    rank1 = np.linalg.matrix_rank(a)
    rank2 = np.linalg.matrix_rank(np.append(a, [np.array(b)], axis=0))
    if rank1 != rank2:
        print('No solution')
    else:
        if rank1 < (len(dict.keys()) -1):
            dimension = len(dict.keys())-1-rank1
            print('Solution space dimension: ', dimension)
        else:
            # res = np.linalg.det(a)
            # print(res)
            x = np.linalg.solve(a.T,b)
            index = 0
            for key in dict.keys():
                print(key, ' = ', int(x[index]), end=', ', flush=True)


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