#!/usr/bin/python3
import sys
import scorelib
import sqlite3
import json

def search_composers(print_id):
    conn = sqlite3.connect('scorelib.dat')
    # conn.set_trace_callback(print)
    cur = conn.cursor()
    res = cur.execute('SELECT person.name, person.born, person.died FROM person '
                      'JOIN score_author on person.id = score_author.composer '
                      'JOIN edition on edition.score = score_author.score '
                      'JOIN print on edition.id = print.edition WHERE print.id = ?',
                      (print_id,)).fetchall()
    items = []
    if res is not None:
        for person in res:
            item = {}
            item["name"] = person[0]
            if person[1] is not None:
                item["born"] = person[1]
            if person[2] is not None:
                item["died"] = person[2]
            items.append(item)
    print(json.dumps(items))

if __name__ == "__main__":

    if len(sys.argv) == 2:
        search_composers(sys.argv[1])
    else:
        print("Wrong number of arguments")