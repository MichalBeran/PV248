#!/usr/bin/python3
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import json


def get_sum_list(list):
    result = []
    index_sum = 0
    for item in list:
        index_sum += item
        result.append(index_sum)
    return result


def get_student_stats(dataset):
    mean = dataset.mean(axis=1).iloc[0]
    median = dataset.median(axis=1).iloc[0]
    total = dataset.sum(axis=1).iloc[0]
    passed = int(np.sum(dataset > 0, axis=1))
    return mean, median, total, passed


def regression(dataset):
    semester_start = datetime.strptime('2018-09-17', "%Y-%m-%d").date()
    x = [(datetime.strptime(i, "%Y-%m-%d").date() - semester_start).days for i in list(dataset)]
    # x = [0]+x
    y = get_sum_list(list(dataset.iloc[0]))
    # y = [0]+y
    x = np.array(x)
    y = np.array(y)
    xi = x[:, np.newaxis]
    slope, _, _, _ = np.linalg.lstsq(xi, y, rcond=None)
    slope = slope[0]
    if slope != 0:
        sixteen = str(semester_start + timedelta(16 / slope))
        twenty = str(semester_start + timedelta(20 / slope))
    else:
        sixteen = None
        twenty = None
    return slope, sixteen, twenty


def student_stat(csv, student_id):
    item = dict()
    data = pd.read_csv(csv)
    # if student_row.count() > 0:
    exercises_regex = '\d{4}-\d{2}-\d{2}\/(\d{2})'
    dates_regex = '(\d{4}-\d{2}-\d{2})\/\d{2}'
    if student_id is not None:
        student_row = data.query('student == ' + student_id)
        exercises_grouped = student_row.groupby(student_row.columns.str.extract(exercises_regex, expand=False), axis=1).sum()

        dates_grouped = student_row.groupby(student_row.columns.str.extract(dates_regex, expand=False), axis=1).sum()
        dates_grouped = dates_grouped.reindex(sorted(dates_grouped.columns), axis=1)
    else:
        exercises_grouped = data.groupby(data.columns.str.extract(exercises_regex, expand=False), axis=1).sum()
        exercises_grouped = exercises_grouped.mean().to_frame(name='exercises').T

        dates_grouped = data.groupby(data.columns.str.extract(dates_regex, expand=False), axis=1).sum()
        dates_grouped = dates_grouped.reindex(sorted(dates_grouped.columns), axis=1).mean().to_frame('points').T
    mean, median, total, passed = get_student_stats(exercises_grouped)
    item['mean'] = mean
    item['median'] = median
    item['total'] = total
    item['passed'] = passed
    slope, sixteen_points_date, twenty_points_date = regression(dates_grouped)
    item['regression slope'] = slope
    if slope != 0:
        item['date 16'] = sixteen_points_date
        item['date 20'] = twenty_points_date
    print(json.dumps(item, ensure_ascii=False, sort_keys=False, indent=4))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if sys.argv[2] == 'average':
            student_stat(sys.argv[1], None)
        else:
            student_stat(sys.argv[1], sys.argv[2])
    else:
        print("Wrong number of arguments")