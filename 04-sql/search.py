#!/usr/bin/python3
import sys
import sqlite3
import json


def search(name):
    conn = sqlite3.connect('scorelib.dat')
    cur = conn.cursor()
    res = cur.execute('SELECT * FROM person WHERE name like ?', ("%" + name + "%",)).fetchall()
    people = {}
    if res is not None:
        for person in res:
            # print(person)
            prints_info = cur.execute('SELECT print.id, print.partiture, score.id, edition.id FROM person '
                          'JOIN score_author on person.id = score_author.composer '
                          'JOIN edition on edition.score = score_author.score '
                          'JOIN score on score.id = edition.score '
                          'JOIN print on edition.id = print.edition WHERE person.id = ?',
                          (person[0],)).fetchall()
            # print(prints_info)
            prints = []
            if prints_info is not None:
                for print_info_item in prints_info:
                    print_item = {}
                    print_item["Print Number"] = print_info_item[0]
                    if print_info_item[1] == 'Y':
                        print_item["Partiture"] = True
                    else:
                        print_item["Partiture"] = False
                    composition_info_item = cur.execute('SELECT * FROM score WHERE id=?',
                                                        (print_info_item[2],)).fetchone()
                    edition_info_item = cur.execute('SELECT * FROM edition WHERE id=?',
                                                        (print_info_item[3],)).fetchone()
                    if composition_info_item is not None:
                        print_item["Title"] = composition_info_item[1]
                        if composition_info_item[2] is not None:
                            print_item["Genre"] = composition_info_item[2]
                        if composition_info_item[3] is not None:
                            print_item["Key"] = composition_info_item[3]
                        if composition_info_item[4] is not None:
                            print_item["Incipit"] = composition_info_item[4]
                        if composition_info_item[5] is not None:
                            print_item["Composition Year"] = composition_info_item[5]
                    if edition_info_item is not None:
                        if edition_info_item[2] is not None:
                            print_item["Edition"] = edition_info_item[2]
                    composer_info_items = cur.execute(
                        'SELECT * FROM person JOIN score_author on person.id = score_author.composer '
                        'WHERE score_author.score=?', (print_info_item[2],)).fetchall()
                    if composer_info_items is not None:
                        composers = []
                        for composer_info_item in composer_info_items:
                            composer_item = {}
                            composer_item["Name"] = composer_info_item[3]
                            if composer_info_item[1] is not None:
                                composer_item["Born"] = composer_info_item[1]
                            if composer_info_item[2] is not None:
                                composer_item["Died"] = composer_info_item[2]
                            composers.append(composer_item)
                        print_item["Composer"] = composers
                    editor_info_items = cur.execute(
                        'SELECT * FROM person JOIN edition_author on person.id = edition_author.editor '
                        'WHERE edition_author.edition=?', (print_info_item[3],)).fetchall()
                    if editor_info_items is not None:
                        editors = []
                        for editor_info_item in editor_info_items:
                            editor_item = {}
                            editor_item["Name"] = editor_info_item[3]
                            if editor_info_item[1] is not None:
                                editor_item["Born"] = editor_info_item[1]
                            if editor_info_item[2] is not None:
                                editor_item["Died"] = editor_info_item[2]
                            editors.append(editor_item)
                        print_item["Editor"] = editors
                    voice_info_items = cur.execute(
                        'SELECT * FROM voice WHERE score=?', (print_info_item[2],)).fetchall()
                    if voice_info_items is not None:
                        voices = {}
                        for voice_info_item in voice_info_items:
                            voice_item = {}
                            if voice_info_item[3] is not None:
                                voice_item["range"] = voice_info_item[3]
                            if voice_info_item[4] is not None:
                                voice_item["name"] = voice_info_item[4]
                            voices[voice_info_item[1]] = voice_item
                        print_item["Voices"] = voices
                    prints.append(print_item)
            people[person[3]] = prints

    print(json.dumps(people, ensure_ascii=False, sort_keys=True, indent=4))

if __name__ == "__main__":

    if len(sys.argv) == 2:
        search(sys.argv[1])
    else:
        print("Wrong number of arguments")