import contextlib
from collections import UserDict
from datetime import datetime
import pickle
import time
from faker import Faker
import random
import os.path
from prettytable import PrettyTable, NONE, ALL
from termcolor import colored, cprint
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion


class IntentCompleter(Completer):
    def __init__(self, commands):
        super().__init__()
        self.intents = commands

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = text_before_cursor.split()[-1] if text_before_cursor else ''

        for intent in self.intents:
            if intent.startswith(word_before_cursor):
                yield Completion(intent, start_position=-len(word_before_cursor))


class Notes(UserDict):
    filename = 'notes.sav'
    MAX_STR_LEN = 50

    def add_note(self, note):
        id = self.new_id()
        note = Note(note, id)
        self.data[note.id] = note

    def new_id(self):
        if not self.data:
            return 1
        else:
            id_list = list(self.data.keys())
            id_list.sort()
            id = id_list[-1:][0] + 1
            return id

    def find_in_notes(self, string):
        res = {}
        for k, v in self.data.items():
            if v.text.lower().find(string.lower()) >= 0:
                res[k] = v
        return res

    def edit_note(self, note, id):
        self.data[id].edit_note(note)

    def del_note(self, id):
        self.data.pop(id)

    def add_tags(self, id, tags):
        if id in self.data.keys():
            self.data[id].add_note_tags(tags)
            
    def find_by_tag(self, string):
        res = {}
        for k, v in self.data.items():
            if string.lower() in v.tags:
                res[k] = v
        return res

    def show_notes(self, data = None):
        l = self.MAX_STR_LEN
        if not data:
            data = self.data
        x = PrettyTable(align='l', header=False, vrules=NONE)
        for k, v in data.items():
            note = ''
            t = v.text
            while len(t):
                note += colored(t[:l],'blue') + '\n'
                t = t[l:]
            if v.tags:
                note += colored(v.show_tags(),'light_cyan') + '\n'
            dt = v.datetime.strftime("<%d-%m-%Y %H:%M>")
            note += colored(dt + ' ' * 25 + 'id: ' + str(k), 'grey')
            x.add_row([note], divider=True)
        return x

    def iterator(self, step=5):
        data = list(self.data.values())
        while data:
            res = data[:step]
            data = data[step:]
            yield res

    def save_to_file(self):
        with open(self.filename, "wb") as file:
            pickle.dump(self, file)

    def read_from_file(self):
        with open(self.filename, "rb") as file:
            content = pickle.load(file)
        return content


class Note:
    MAX_NOTE_LEN = 150   # max lenth of note

    def __init__(self, note, id):
        self.text = note[:self.MAX_NOTE_LEN]
        self.tags = set()
        self.datetime = datetime.now()
        self.id = id

    def add_note_tags(self, tags):
        self.tags.update(tags.split())

    def del_tag(self, tag):
        self.tags.remove(tag)

    def show_tags(self):
        return '#' + ', #'.join(self.tags)

    def edit_note(self, new_text):
        self.text = new_text


def fake_notes(notes):
    fake = Faker(('uk_UA'))
    notes.add_note('Заметка о том, что нужно не забыть делать заметки, чтобы ничего не забывать :-)')
    time.sleep(0.1)
    for _ in range(10):
        i = random.randint(45, 210)
        notes.add_note(fake.text(i))
        time.sleep(0.1)


def show_greeting(commands):
    x = PrettyTable(align='l') 
    x.field_names = [colored("Доступні команди:", 'light_blue')]
    for a, i in enumerate(commands, start=1):
        x.add_row([colored(f"{a}. {i}","blue")])     
    return x


def main():
    PROMPT = ' > '    #приглашение командной строки
    commands = ['add', 'show', 'find', 'edit', 'tag', 'tagfind', 'exit']
    session = PromptSession(auto_suggest=AutoSuggestFromHistory(), 
                            completer=IntentCompleter(commands))
    
    notes = Notes()
    if not os.path.exists(notes.filename):
        fake_notes(notes)
    else:
        notes = notes.read_from_file()

    print(show_greeting(commands))

    while True:
        answer = session.prompt('Введіть команду' + PROMPT).strip()
        d, *args = answer.split(' ')
        with contextlib.suppress(ValueError):
            if int(d):
                for a, i in enumerate(commands, start=1):
                    if a == int(d):
                        d = i
        if answer == 'add' or d == 'add':     #добавление заметки
            note = input("Введіть свою нотатку" + PROMPT)
            if note:
                notes.add_note(note)
                notes.save_to_file()
                print("Вашу нотатку додано", 'green')
        elif answer == "show" or d == 'show':  #вывод всех заметок
            print(notes.show_notes())
        elif answer == "find" or d == 'find':  #поиск по заметкам
            string = input("Що знайти" + PROMPT)
            res = notes.find_in_notes(string)
            if not len(res):
                cprint("Співпадінь не знайдено", 'green')
            else:
                print(notes.show_notes(res))
        elif answer == "edit" or d == 'edit':  #редактирование заметки
            id = int(input("Введіть id нотатки" + PROMPT))
            print(notes.show_notes({id: notes.data[id]}))
            note = input("Введіть новий текст" + PROMPT)
            notes.edit_note(note, id)
            notes.save_to_file()
            cprint("Нотатку змінено", 'green')
        elif answer == "tag" or d == 'tag':  #добавление тегов в заметку
            id = int(input("Введіть id нотатки" + PROMPT))
            print(notes.show_notes({id: notes.data[id]}))
            note = input("Введіть тег" + PROMPT)
            notes.add_tags(id, note)
            notes.save_to_file()
            cprint("Тег додано", 'green')
        elif answer == "tagfind" or d == 'tagfind':   #поиск по тегу
            string = input("Який тег знайти" + PROMPT)
            res = notes.find_by_tag(string)
            if not len(res):
                cprint("Співпадінь не знайдено", 'green')
            else:
                print(notes.show_notes(res))
        elif answer == "del" or d == 'del':  #удаление заметки
            id = int(input("Введіть id нотатки" + PROMPT))
            notes.del_note(id)
            notes.save_to_file()
            cprint("Нотатку видалено", 'green')
        elif answer in ["exit", ""] or d == 'exit':    #выход из цикла
            notes.save_to_file()
            cprint('See you soon!', 'green')
            break    
    pass


if __name__ == "__main__":
    main()