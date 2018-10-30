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
            print('solution space dimension: ', dimension)
        else:
            # res = np.linalg.det(a)
            # print(res)
            x = np.linalg.solve(a,b)
            print('solution: ', end='')
            index = 0
            for key in sorted(dict):
                print(key, ' = ', x[index], end='', flush=True)
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