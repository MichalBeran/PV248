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
        select_composition_query = 'SELECT id FROM score WHERE'
        select_composition_params = []
        if composition.name is not None:
            select_composition_query += ' name=?'
            select_composition_params.append(composition.name)
        else:
            select_composition_query += ' name is null'
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

        composition_id = None
        select_composition = cur.execute(
            select_composition_query,
            select_composition_params).fetchall()
        if select_composition is not None:
            if len(select_composition) > 0:
                for selected_composition in select_composition:
                    difference = False
                    composition_voices = cur.execute('SELECT number, range, name FROM voice WHERE score=?',
                                                     (selected_composition[0], )).fetchall()
                    if len(composition_voices) == len(composition.voices):
                        index = 0
                        while index < len(composition.voices):
                            if composition_voices[index][0] != composition.voices[index].number or composition_voices[index][1] != composition.voices[index].range or composition_voices[index][2] != composition.voices[index].name:
                                difference = True
                            index += 1
                    else:
                        difference = True
                    composition_composers = cur.execute('SELECT person.name FROM person JOIN score_author on '
                                                        'person.id = score_author.composer WHERE score_author.score=?',
                                                     (selected_composition[0], )).fetchall()
                    if len(composition_composers) == len(composition.authors):
                        index = 0
                        while index < len(composition.authors):
                            if composition_composers[index][0] != composition.authors[index].name:
                                difference = True
                            index += 1
                    else:
                        difference = True
                    if not difference:
                        composition_id = selected_composition[0]
                        # print(composition.name, composition_id)

        if composition_id is None:
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
        if edition.name is None:
            select_edition = cur.execute('SELECT id FROM edition WHERE name is null AND score=?',
                                         (composition_id,)).fetchall()
        else:
            select_edition = cur.execute('SELECT id FROM edition WHERE name=? AND score=?',
                                         (edition.name, composition_id, )).fetchall()
        edition_id = None
        if select_edition is not None:
            if len(select_edition) > 0:
                for selected_edition in select_edition:

                    difference = False
                    edition_editors = cur.execute('SELECT person.name FROM person JOIN edition_author on '
                                                  'person.id = edition_author.editor WHERE edition_author.edition=?',
                                                  (selected_edition[0], )).fetchall()
                    if len(edition_editors) == len(edition.authors):
                        index = 0
                        while index < len(edition.authors):
                            if edition_editors[index][0] != edition.authors[index].name:
                                difference = True
                            index += 1
                    else:
                        difference = True
                    if not difference:
                        edition_id = selected_edition[0]

        if edition_id is None:
            edition_id = cur.execute('INSERT INTO edition (score, name, year) VALUES (?, ?, ?)',
                                     (composition_id, edition.name, None)).lastrowid

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
        # os.remove(str(sys.argv[2]))
        # only for tests
        save_to_db(sys.argv[1], sys.argv[2])
    else:
        print("Wrong number of arguments")