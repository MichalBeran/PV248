#!/usr/bin/python3
import re


def parse_people(string):
    splitted = string.split(';')
    result_list = []
    for p in splitted:
        person = Person()
        dates = re.search(r"\((\d{4}|) -- (\d{4}|)\)", p)
        only_birth = re.search(r"\*.*?(\d{4})", p)
        only_death = re.search(r"\+.*?(\d{4})", p)
        if dates is not None:
            if dates.group(1) is not None:
                if dates.group(1) is not '':
                    person.born = int(dates.group(1))
            if dates.group(2) is not None:
                if dates.group(2) is not '':
                    person.died = int(dates.group(2))
        elif only_birth is not None:
            person.born = int(only_birth.group(1))
        elif only_death is not None:
            person.died = int(only_death.group(1))
        person.name = re.sub(r"^\s*", '', re.sub(r"\s*$", '', re.sub(r"\(.*?\)", '', p)))
        result_list.append(person)
    return result_list


def get_people_string(people):
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
    return '; '.join(str(item) for item in result_list)


def match_bool(string):
    if(string == "yes"):
        return True
    if (string == "no"):
        return False


def load(file):
    f = open(file, 'r', encoding='utf8')
    lines = f.read()
    result_list = []
    for one_print in lines.split("\n\n"):
        # parse voices
        voices = []
        for voices_match in re.finditer(r"Voice (.*): ((.*?--.*?)[,|;] (.*)|(.*))", one_print):
            voice = Voice()
            if voices_match.group(5) is not None:
                voice.name = voices_match.group(4)
            elif voices_match.group(5) is not None:
                voice.name = voices_match.group(4)
            if voices_match.group(3) is not None:
                voice.range = voices_match.group(3)
            voices.append(voice)
        # parse composition
        composition = Composition()
        composition_name_string = re.search(r"Title: (.*)", one_print)
        if composition_name_string is not None:
            composition.name = composition_name_string.group(1)
        incipit_string = re.search(r"Incipit: (.*)", one_print)
        if incipit_string is not None:
            composition.incipit = incipit_string.group(1)
        key_string = re.search(r"Key: (.*)", one_print)
        if key_string is not None:
            composition.key = key_string.group(1)
        genre_string = re.search(r"Genre: (.*)", one_print)
        if genre_string is not None:
            composition.genre = genre_string.group(1)
        composition_year_string = re.search(r"Composition Year: (\d{3,4})", one_print)
        if composition_year_string is not None:
            composition.year = int(composition_year_string.group(1))
        composition.authors = parse_people(re.search(r"Composer: (.*)", one_print).group(1))
        composition.voices = voices
        # parse edition
        edition = Edition()
        edition_name_string = re.search(r"Edition: (.*)", one_print)
        if edition_name_string is not None:
            edition.name = edition_name_string.group(1)
        authors_string = re.search(r"Editor: (.*)", one_print)
        if authors_string is not None:
            edition.authors = parse_people(authors_string.group(1))
        edition.composition = composition
        # parse print
        print_obj = Print()
        print_obj.print_id = re.sub(r"\(.*?\)", '',
                                re.sub(r"\s*$", '', re.search(r"Print Number: (.*)", one_print).group(1)))
        print_obj.edition = edition
        print_obj.partiture = match_bool(re.search(r"Partiture: (.*)", one_print).group(1))
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
        print("Composer: " + get_people_string(self.edition.composition.authors))
        print("Title: " + self.edition.composition.name)
        if self.edition.composition.genre is not None:
            print("Genre: " + self.edition.composition.genre)
        if self.edition.composition.key is not None:
            print("Key: " + self.edition.composition.key)
        if self.edition.composition.year is not None:
            print("Composition Year: " + str(self.edition.composition.year))
        # print("Publication Year: ")
        if self.edition.name is not None:
            print("Edition: " + self.edition.name)
        print("Editor: " + get_people_string(self.edition.authors))
        index = 1
        for voice in self.edition.composition.voices:
            voice_string = ''
            if voice.range is not None:
                voice_string += voice.range
                if voice.name is not None:
                    voice_string += ', '
            elif voice.name is not None:
                voice_string += voice.name
            print("Voice " + str(index) + ": " + voice_string)
            index += 1
        if self.partiture:
            print("Partiture: yes")
        else:
            print("Partiture: no")
        if self.edition.composition.incipit is not None:
            print("Incipit: " + self.edition.composition.incipit)
        print()