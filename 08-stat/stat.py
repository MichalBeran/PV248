#!/usr/bin/python3

import sys
import numpy as np
import pandas as pd
import json


def load_data_frame(csv):
    return pd.read_csv(csv)


def get_group_stats(group):
    json_item = {}
    sum_stat = group.sum(axis=1)
    json_item['mean'] = sum_stat.mean()
    json_item['median'] = sum_stat.median()
    json_item['first'] = sum_stat.quantile(0.25)
    json_item['last'] = sum_stat.quantile(0.75)
    json_item['passed'] = int(np.sum(sum_stat > 0))
    return json_item


def print_grouped_stats(grouped):
    items = {}
    for name, group in grouped:
        items[name] = get_group_stats(group)
    print(json.dumps(items, ensure_ascii=False, sort_keys=False, indent=4))


def date_stat(csv):
    data = load_data_frame(csv)
    regex = '(\d{4}-\d{2}-\d{2})\/\d{2}'
    # print(data)
    grouped = data.groupby(data.columns.str.extract(regex, expand=False), axis=1)
    print_grouped_stats(grouped)


def deadline_stat(csv):
    data = load_data_frame(csv)
    regex = '(\d{4}-\d{2}-\d{2}\/\d{2})'
    # print(data)
    grouped = data.groupby(data.columns.str.extract(regex, expand=False), axis=1)
    print_grouped_stats(grouped)


def exercises_stat(csv):
    data = load_data_frame(csv)
    regex = '\d{4}-\d{2}-\d{2}\/(\d{2})'
    # print(data)
    grouped = data.groupby(data.columns.str.extract(regex, expand=False), axis=1)
    print_grouped_stats(grouped)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if sys.argv[2] == 'dates':
            date_stat(sys.argv[1])
        elif sys.argv[2] == 'deadlines':
            deadline_stat(sys.argv[1])
        elif sys.argv[2] == 'exercises':
            exercises_stat(sys.argv[1])
        else:
            print("unknown parameter:", sys.argv[2])
    else:
        print("Wrong number of arguments")