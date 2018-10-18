#!/usr/bin/python3
import re


def parse_people(string, splitter):
    splitted = []
    if splitter == ',':
        splitted_first = string.split(',')
        enum = enumerate(splitted_first)
        index, item = next(enum, (None, None))
        while item is not None:
            person = '' + item
            index, item = next(enum, (None, None))
            if item is not None:
                person += ','
                person += item
            splitted.append(person)
            index, item = next(enum, (None, None))
    else:
        splitted = string.split(';')
    result_list = []
    for p in splitted:
        person = Person()
        birth_date = re.search(r"\((\d{4})\s?-.*?\)", p)
        death_date = re.search(r"\(.*?-\s?(\d{4})\)", p)
        only_birth = re.search(r"\*.*?(\d{4})", p)
        only_death = re.search(r"\+.*?(\d{4})", p)
        if birth_date is not None:
            person.born = int(birth_date.group(1))
        elif only_birth is not None:
            person.born = int(only_birth.group(1))
        if death_date is not None:
            person.died = int(death_date.group(1))
        elif only_death is not None:
            person.died = int(only_death.group(1))
        person.name = re.sub(r"^\s*", '', re.sub(r"\s*$", '', re.sub(r"\(.*?\)", '', p)))
        if person.name is not None:
            if person.name != '':
                result_list.append(person)
    return result_list


def get_people_string(people, separator):
    result_list = []
    for person in people:
        person_string = ""
        person_string += person.name
        if person.born is not None or person.died is not None:
            person_string += " ("
            if person.born is not None:
                person_string += str(person.born)
            person_string += "--"
            if person.died is not None:
                person_string += str(person.died)
            person_string += ")"
        result_list.append(person_string)
    return str(separator).join(str(item) for item in result_list)


def match_boolean(string):
    if string == 'yes' or string == 'Yes':
        return True
    else:
        return False


def load(file):
    f = open(file, 'r', encoding='utf8')
    lines = f.read()
    result_list = []
    for one_print in lines.split("\n\n"):
        if one_print is None:
            break
        if one_print == '' or one_print == ' ':
            break
        # parse voices
        voices = []
        for voices_match in re.finditer(r"Voice (.*?): ((.*?--.*?)[,|;] (.*)|(.*))", one_print):
            voice = Voice()
            if voices_match.group(1) is not None:
                voice.number = int(voices_match.group(1))
            if voices_match.group(5) is not None:
                voice.name = voices_match.group(5).strip(' ')
            elif voices_match.group(4) is not None:
                voice.name = voices_match.group(4).strip(' ')
            if voices_match.group(3) is not None:
                voice.range = voices_match.group(3)
            voices.append(voice)
        # parse composition
        composition = Composition()
        composition_name_string = re.search(r"Title: (.*)", one_print)
        if composition_name_string is not None:
            composition.name = composition_name_string.group(1).strip(' ')
        incipit_string = re.search(r"Incipit: (.*)", one_print)
        if incipit_string is not None:
            composition.incipit = incipit_string.group(1).strip(' ')
        key_string = re.search(r"Key: (.*)", one_print)
        if key_string is not None:
            composition.key = key_string.group(1).strip(' ')
        genre_string = re.search(r"Genre: (.*)", one_print)
        if genre_string is not None:
            composition.genre = genre_string.group(1).strip(' ')
        composition_year_string = re.search(r"Composition Year: (\d{3,4})", one_print)
        if composition_year_string is not None:
            composition.year = int(composition_year_string.group(1))
        composer_string = re.search(r"Composer: (.*)", one_print)
        if composer_string is not None:
            composition.authors = parse_people(composer_string.group(1), ';')
        composition.voices = voices
        # parse edition
        edition = Edition()
        edition_name_string = re.search(r"Edition: (.*)", one_print)
        if edition_name_string is not None:
            edition.name = edition_name_string.group(1).strip(' ')
        authors_string = re.search(r"Editor: (.*)", one_print)
        if authors_string is not None:
            edition.authors = parse_people(authors_string.group(1), ',')
        edition.composition = composition
        # parse print
        print_obj = Print()
        print_obj.print_id = int(re.sub(r"\(.*?\)", '',
                                re.sub(r"\s*$", '', re.search(r"Print Number: (.*)", one_print).group(1))))
        print_obj.edition = edition
        print_obj.partiture = match_boolean(re.search(r"Partiture: (yes|no|Yes|No|.*?)", one_print).group(1))
        result_list.append(print_obj)

    result_list.sort(key=lambda x: int(x.print_id))
    return result_list


class Person:
    def __init__(self):
        self.name = None
        self.born = None
        self.died = None


class Voice:
    def __init__(self):
        self.name = None
        self.range = None
        self.number = 0


class Composition:
    def __init__(self):
        self.name = None
        self.incipit = None
        self.key = None
        self.genre = None
        self.year = None
        self.voices = []
        self.authors = []


class Edition:
    def __init__(self):
        self.composition = Composition()
        self.authors = []
        self.name = ""


class Print:
    def __init__(self):
        self.edition = Edition()
        self.print_id = None
        self.partiture = False

    def composition(self):
        return self.edition.composition

    def format(self):
        print("Print Number: " + str(self.print_id))
        print("Composer: " + get_people_string(self.edition.composition.authors, '; '))
        print("Title: " + self.edition.composition.name)
        genre_string = "Genre: "
        if self.edition.composition.genre is not None:
            genre_string += self.edition.composition.genre
        print(genre_string)
        key_string = "Key: "
        if self.edition.composition.key is not None:
            key_string += self.edition.composition.key
        print(key_string)
        composition_year_string = "Composition Year: "
        if self.edition.composition.year is not None:
            composition_year_string += str(self.edition.composition.year)
        print(composition_year_string)
        # print("Publication Year: ")
        edition_name_string = "Edition: "
        if self.edition.name is not None:
            edition_name_string += self.edition.name
        print(edition_name_string)
        print("Editor: " + get_people_string(self.edition.authors, ', '))
        index = 1
        for voice in self.edition.composition.voices:
            voice_string = ''
            if voice.range is not None:
                voice_string += voice.range
                if voice.name is not None:
                    voice_string += ', '
            if voice.name is not None:
                voice_string += voice.name
            print("Voice " + str(index) + ": " + voice_string)
            index += 1
        if self.partiture:
            print("Partiture: yes")
        else:
            print("Partiture: no")
        incipit_string = "Incipit: "
        if self.edition.composition.incipit is not None:
            incipit_string += self.edition.composition.incipit
        print(incipit_string)
        print()