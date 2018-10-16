#!/usr/bin/python3
import sys
import scorelib
import sqlite3
import os


def save_to_db(file, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    db_schema = "create table person ( id integer primary key not null," \
                "                      born integer," \
                "                      died integer," \
                "                      name varchar not null );"
    db_schema += "create table score ( id integer primary key not null," \
                 "                     name varchar," \
                 "                     genre varchar," \
                 "                     key varchar," \
                 "                     incipit varchar," \
                 "                     year integer );"
    db_schema += "create table voice ( id integer primary key not null," \
                 "                     number integer not null," \
                 "                       score integer references score( id ) not null,range varchar," \
                 "                     name varchar );"
    db_schema += "create table edition ( id integer primary key not null," \
                 "                       score integer references score( id ) not null," \
                 "                       name varchar," \
                 "                       year integer );"
    db_schema += "create table score_author( id integer primary key not null," \
                 "                           score integer references score( id ) not null," \
                 "                           composer integer references person( id ) not null );"
    db_schema += "create table edition_author( id integer primary key not null," \
                 "                             edition integer references edition( id ) not null," \
                 "                             editor integer references person( id ) not null );"
    db_schema += "create table print ( id integer primary key not null," \
                 "                     partiture char(1) default 'N' not null," \
                 "                     edition integer references edition( id ) );"
    # f = open('./scorelib.sql', 'r', encoding='utf8')
    # cur.executescript(f.read())
    # f.close()
    cur.executescript(db_schema)
    list = scorelib.load(file)
    for item in list:
        # import composition / score
        composition = item.edition.composition
        select_composition_query = 'SELECT id FROM score WHERE name=?'
        select_composition_params = []
        select_composition_params.append(composition.name)
        if composition.genre is not None:
            select_composition_query += ' AND genre=?'
            select_composition_params.append(composition.genre)
        else:
            select_composition_query += ' AND genre is null'
        if composition.key is not None:
            select_composition_query += ' AND key=?'
            select_composition_params.append(composition.key)
        else:
            select_composition_query += ' AND key is null'
        if composition.incipit is not None:
            select_composition_query += ' AND incipit=?'
            select_composition_params.append(composition.incipit)
        else:
            select_composition_query += ' AND incipit is null'
        if composition.year is not None:
            select_composition_query += ' AND year=?'
            select_composition_params.append(composition.year)
        else:
            select_composition_query += ' AND year is null'

        select_composition = cur.execute(
            select_composition_query,
            select_composition_params).fetchone()
        if select_composition is not None:
            composition_id = select_composition[0]
        else:
            composition_id = cur.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                                     (composition.name, composition.genre, composition.key, composition.incipit,
                                      composition.year)).lastrowid
        # import composition authors
        authors = item.edition.composition.authors
        for author in authors:
            select = cur.execute('SELECT id FROM person WHERE name=?', (author.name,))
            existing_author_id = select.fetchone()
            if existing_author_id is None:
                author_id = cur.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)',
                                        (author.name, author.born, author.died)).lastrowid
                # print(author_id, author.name)
            else:
                if author.born is not None:
                    cur.execute('UPDATE person SET born=? WHERE id=?', (author.born, existing_author_id[0]))
                    # print('updated person born', author.name, author.born)
                if author.died is not None:
                    cur.execute('UPDATE person SET died=? WHERE id=?', (author.died, existing_author_id[0]))
                    # print('updated person died', author.name, author.died)
                # print(author.name)
                author_id = existing_author_id[0]
            # score - author
            cur.execute('INSERT INTO score_author (score, composer) VALUES (?, ?)',
                        (composition_id, author_id)).lastrowid
        # import voices
        voices = item.edition.composition.voices
        for voice in voices:
            voice_id = cur.execute('INSERT INTO voice (number, score, range, name) VALUES (?, ?, ?, ?)',
                                    (voice.number, composition_id, voice.range, voice.name)).lastrowid
        # import edition
        edition = item.edition
        select_edition = cur.execute('SELECT id FROM edition WHERE name=? AND score=?', (edition.name, composition_id, )).fetchone()
        # edition_id = cur.execute('INSERT INTO edition (score, name, year) VALUES (?, ?, ?)',
        #                          (composition_id, edition.name, None)).lastrowid

        if select_edition is None:
            edition_id = cur.execute('INSERT INTO edition (score, name, year) VALUES (?, ?, ?)',
                                     (composition_id, edition.name, None)).lastrowid
        else:
            # print('duplicite edition', select_edition[0], edition.name)
            edition_id = select_edition[0]

        # import editors
        editors = item.edition.authors
        for editor in editors:
            select = cur.execute('SELECT id FROM person WHERE name=?', (editor.name,))
            existing_editor_id = select.fetchone()
            if existing_editor_id is None:
                editor_id = cur.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)',
                                        (editor.name, editor.born, editor.died)).lastrowid
                # print(editor_id, editor.name)
            else:
                if editor.born is not None:
                    cur.execute('UPDATE person SET born=? WHERE id=?', (editor.born, existing_editor_id[0]))
                    # print('updated person born', editor.name, editor.born)
                if editor.died is not None:
                    cur.execute('UPDATE person SET died=? WHERE id=?', (editor.died, existing_editor_id[0]))
                    # print('updated person died', editor.name, editor.died)
                # print(editor.name)
                editor_id = existing_editor_id[0]
            # edition - author
            cur.execute('INSERT INTO edition_author (edition, editor) VALUES (?, ?)',
                        (edition_id, editor_id)).lastrowid
        # import print
        if item.partiture:
            partiture = 'Y'
        else:
            partiture = 'N'
        print_id = cur.execute('INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)',
                               (item.print_id, partiture, edition_id)).lastrowid
    conn.commit()

if __name__ == "__main__":

    if len(sys.argv) == 3:
        # only for tests
        os.remove(str(sys.argv[2]))
        # only for tests
        save_to_db(sys.argv[1], sys.argv[2])
    else:
        print("Wrong number of arguments")