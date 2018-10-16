#!/usr/bin/python3
import sys
import scorelib
import sqlite3


def search(name):
    conn = sqlite3.connect('scorelib.dat')
    cur = conn.cursor()
    res = cur.execute('SELECT * FROM person WHERE name like ?', ("%" + name + "%",)).fetchall()
    if res is not None:
        for person in res:
            print(person)
            prints = cur.execute('SELECT print.id, score.name FROM person '
                          'JOIN score_author on person.id = score_author.composer '
                          'JOIN edition on edition.score = score_author.score '
                          'JOIN score on score.id = edition.score '
                          'JOIN print on edition.id = print.edition WHERE person.id = ?',
                          (person[0],)).fetchall()
            print(prints)
            # print(scorelib.Person(person).name)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        search(sys.argv[1])
    else:
        print("Wrong number of arguments")