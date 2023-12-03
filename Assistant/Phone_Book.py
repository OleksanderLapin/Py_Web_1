import contextlib
from collections import UserDict, UserList
from datetime import date, datetime
import pickle
import re
from prettytable import PrettyTable
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


class AddressBook(UserDict):
    def __init__(self, data={}):
        self.data = data
        self.index = 0
        self.__iterator = None
        
    def add_record(self, record):
        self.data[record.name.value] = record

    def del_phone(self, args):
        if args[0] not in self.data.keys():
            return f'Контакт {args[0]} відсутній'
        elif len(args) == 2:
            for key, values in self.data.items():
                if args[0] == key and len(values.phones) != 0:
                        for phone in values.phones:
                            if args[1] == phone.value:
                                values.phones.remove(phone)
                                return f'Номер {phone} видалено!'
                        return f'Номер {args[1]} незнайдено!'
                return f'Контакт {args[0]} немає номерів!'
        else:
            return "Введіть Ім'я та Телефон"
                # return f'Контакт: {args[0]} номери: {j.phones}'
            
    def show_phones(self, args):
        if args:
            if args[0] not in self.data.keys():
                return f'Контакт {args[0]} відсутній'
            for i, j in self.data.items():
                if args[0] == i:
                    return f'Контакт: {args[0]} номери: {str(j.phones)[1:-1]}'
        return "Введіть ім'я контакту"

    def iterator(self):
        if not self.__iterator:
            self.__iterator = iter(self)
        return self.__iterator

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            self.index = 0
            return 'Останній контакт!'
        else:
            result = list(self.data)[self.index]
            self.index += 1
            return result

    def search_in(self, args):
        search_result = []
        for i, j in self.data.items():
            if args[0] in str(self.data[i]):
                search_result.append(self.data[i])
            else:
                for j in list(self.data[i].phones):
                    if args[0] in str(j):
                        search_result.append(self.data[i])
                        break
        x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 
        x.field_names = [colored("Ім'я", 'light_blue'),colored("Телефон", 'light_blue'),colored("Пошта", 'light_blue'),colored("День народження", 'light_blue'),colored("Адреса", 'light_blue')]
        # for values in search_result:
        #     a = ''.join(f'{i}\n' for i in values.phones)
        #     x.add_row([colored(f"{values.name}","blue"),colored(f"{a}","blue"), colored(f"{values.email}","blue"), colored(f"{values.birthday}","blue"), colored(f"{values.address}","blue")])
        # return x
        for values in search_result:
            x.add_row([colored(f"{values.name}","blue"),colored(f"{str(values.phones)[1:-1]}","blue"), colored(f"{values.email}","blue"), colored(f"{values.birthday}","blue"), colored(f"{values.address}","blue")])
        return x
        
    def add_contact(self, args):
        name = args[0]
        
        if self.data.get(name):
            return "Такий контакт вже існує"
        record = Record(Name(name))
        for item in args[1:]:
            if item.startswith("bd="):
                birthday_value = item.split("=")[1]
                record.add_birthday(Birthday(birthday_value)) 
            elif item.startswith("em="):
                mail_value = item.split("=")[1]
                record.add_mail(Email(mail_value)) 
            elif item.startswith("addr="):
                addr_value = item.split("=")[1]
                record.add_address(Address(addr_value))
            else:
                record.add_phone(Phone(item))
        
        self.add_record(record)
        return f'Контакт : {name}, створений'

    def delete_contact(self, contact_name):
        """     5555
        Deletes a contact record based on the provided contact_name.
        If the contact is found and deleted, it returns "Contact deleted".
        If the contact is not found, it returns "Contact not found".
        """
        if self.data.get(contact_name):
            del self.data[contact_name]
            return "Контакт успішно видалений"
        else:
            return "Контакт не знайдено"

    def edit_contact(self, contact_name):
        """
        Edit a contact.
        """
        contact_to_change = self.data.get(contact_name)
        if contact_to_change:
            list_commands = ['done']
            cprint ("+---------------------+", 'blue')
            cprint ("Доступні поля для зміни", 'blue')
            for key, value  in contact_to_change.__dict__.items():
                print(f'{key} - {value}')
                list_commands.append(key)
            cprint ("+---------------------+", 'blue')
            session = PromptSession(auto_suggest=AutoSuggestFromHistory(), completer=IntentCompleter(list_commands))
            while True:
                input = session.prompt('Введіть перші літери поля яке хочете змінити, або "done" щоб завершити редагування > ')
                input = input.split(' ')[0].strip()
                if input == 'done':
                    break
                else:
                    session2 = PromptSession(auto_suggest=AutoSuggestFromHistory(), completer=IntentCompleter([]))
                    if input == 'phones':
                        if len(contact_to_change.phones):
                            text = f'Введіть старий і новий номер у форматі "380XXXXXXXXX" > '
                            new_value = session2.prompt(text)
                            input_phone = new_value.split(' ')
                            contact_to_change.change_phone(input_phone[0], input_phone[1])
                        else:
                            text = f'Введіть номер телефону який хочете додати у форматі "380XXXXXXXXX" > '
                            new_value = session2.prompt(text)
                            input_phone = new_value.split(' ')
                            contact_to_change.add_phone(Phone(input_phone[0]))
                    elif input == 'email':
                        text = f'Введіть новий email y форматі "first@domen.com" > '
                        new_value = session2.prompt(text)
                        input_phone = new_value.split(' ')
                        contact_to_change.change_email_iner(Email(input_phone[0]))
                    elif input == 'birthday':
                        text = f'Введіть дату народження у форматі "День/Місяць/Рік" > '
                        new_value = session2.prompt(text)
                        input_phone = new_value.split(' ')
                        contact_to_change.change_birthday_in(Birthday(input_phone[0]))
                    elif input == 'address':
                        text = f'Введіть нову адресу > '
                        new_value = session2.prompt(text)
                        contact_to_change.change_address_iner(Address(new_value))
                    elif input == 'name':
                        cprint('Вибачте зміна імені не доступна', 'red')

            cprint ("Контакт успішно оновлено", 'green')
        else:
            cprint ("Контакт не знайдено", 'red')
    
    def birthday_in_days(self, args): #add 82-113
        not_cont_with_birthday=True
        for key, value in self.data.items():
            if value.birthday:
                number = int(args[0])
                today = date.today()
                birthday_this_year = date(today.year, value.birthday.value.month, value.birthday.value.day)
                birthday_next_year = date(today.year + 1, value.birthday.value.month, value.birthday.value.day)
                if birthday_this_year >= today:
                    delta = birthday_this_year - today
                    delta_plus = abs(delta.days)
                    if number >= delta_plus:
                        print(f"У {key} день народження через {delta_plus} днів ")
                        not_cont_with_birthday = False
                        continue
                if birthday_next_year >= today:
                    delta = birthday_next_year - today
                    delta_plus = abs(delta.days)
                    if number >= delta_plus:
                        print(f"У {key} день народження через {delta_plus} днів ")
                        not_cont_with_birthday = False
                        continue
        if not_cont_with_birthday:
            cprint("В цей проміжок немає днів народження", 'red')

    def show_all_cont(self):
        x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 
        x.field_names = [colored("Ім'я", 'light_blue'),colored("Телефон", 'light_blue'),colored("Пошта", 'light_blue'),colored("День народження", 'light_blue'),colored("Адреса", 'light_blue')]
        # for i, values in self.data.items():            
        #     a = ''.join(f'{i}\n' for i in values.phones)
        #     x.add_row([colored(f"{i}","blue"),colored(f"{a}","blue"), colored(f"{values.email}","blue"), colored(f"{values.birthday}","blue"), colored(f"{values.address}","blue")])
        # return x
        
        for key, values in self.data.items():
            x.add_row([colored(f"{key}","blue"),colored(f"{str(values.phones)[1:-1]}","blue"),colored(f"{values.email}","blue"), colored(f"{values.birthday}","blue"), colored(f"{values.address}","blue")])
        return x
    
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


class Name(Field):
    pass

class Address(Field):
    pass

class Phone(Field):
    # pass
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value: str):
        if value == '.':
            self.__value = None
        elif value[0] == '-':
            self.__value = value[1:]
        elif len(value) < 9 or len(value) > 12:
            print(f"Невалідний номер: {value}, повинен містити лише 10-12 цифр.")
            self.__value = None
        else:
            self.__value = value  
    
class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if new_value == '.':
            self.__value = None
        else:
            try:
                self.__value = datetime.strptime(new_value, '%d/%m/%Y').date()
        
            except (ValueError):
                print("Неваліда дата народження: {new_value}, (DD/MM/YYYY)")
                raise ValueError("Invalid data. Enter date in format dd/mm/YYYY")


class Email(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value: str):
        if value == '.':
            self.__value = None
        elif not re.match(r"[a-zA-Z]{1}[\w\.]+@[a-zA-Z]+\.[a-zA-Z]{2,}", value):
            print(f"Невалідний email: {value}. Приклад name@domain.com")
            raise ValueError()
        else:
            self.__value = value

class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None, email: Email = None, address: Address = None):
        self.name = name
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def __str__(self):
        return f'{self.name} {self.phones} {self.birthday} {self.email} {self.address}'

    def __repr__(self):
        return f'{self.name} {self.phones} {self.birthday} {self.email} {self.address}'


    def add_phone(self, phone: Phone):
        if phone.value:
            self.phones.append(phone)
    
    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday
    
    def add_mail(self, email: Email):
        self.email = email

    def add_address(self, address: Address):
        self.address = address
    
    def show_phones(self):
        return self.phones
    
    def show_birthday(self):
        return self.birthday
    
    def show_email(self):
        return self.email

    def change_phone(self, old_phone : Phone, new_phone : Phone):
        for phone in self.phones:
            if phone == old_phone:
                self.add_phone(new_phone)
                self.phones.remove(phone)
                return f'Номер {del_phone} видалено.'

    def change_birthday_in(self, birthday: Birthday):
        self.birthday = birthday
        return 'Дата народження змінена'
    
    
    def change_email_iner(self, email: Email):
        self.email = email
        return f'{self.email}'
    
    def change_address_iner(self, address: Address):
        self.address = address
        return f'{self.address}'

    def delete_phone(self, new_phone):
        for phone in self.phones:
            if phone == new_phone:
                self.phones.remove(phone)
                # return True

    def days_to_birthday(self):
        if not self.birthday:
            return ' '
        today = date.today()
        birthday_this_year = date(today.year, self.birthday.value.month, self.birthday.value.day)
        if birthday_this_year >= today:
            delta = birthday_this_year - today
        else:
            delta = date(today.year + 1, self.birthday.value.month, self.birthday.value.day) - today
        return delta.days


file_name = 'Address_Book.bin'
# commands = ['add', 'change', 'phones', 'hello', 'show_all', 'next', 'del_phone', 'del_contact', 'change_email', 'change_bd', 'edit_contact', 'search', 'help', 'change_address', 'birthday_in_days', 'exit']
commands = ['add', 'phones', 'show_all', 'next', 'del_phone', 'del_contact', 'edit_contact', 'search', 'birthday_in_days', 'help', 'exit']

def show_help():      
    x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 

    x.field_names = [colored("Робота з адресною книгою, наразі доступні наступні команди:", 'light_blue')]
    for a, i in enumerate(commands, start=1):
        x.add_row([colored(f"{a}. {i}","blue")])
    # x.add_row([colored("0. exit", "blue")])
    return x # показуємо табличку

def pack_data():
    with open(file_name, "wb") as f:
        pickle.dump(phone_book, f)


def unpack_data():
    with open(file_name, "rb") as f:
        unpacked = pickle.load(f)
        global phone_book
        phone_book = unpacked

def input_error(func):
    def inner(*args):
        try: 
            return func(*args)  
        except KeyError:
            print('Enter user name.')
        except ValueError:
            #print('Incorrect data in input.')
            cprint('Некоректні данні', 'red')
        except IndexError:
            #print('You entered not correct number of args')
            cprint('Введіть правильну кількість аргументів', 'red')
        except TypeError:
            print('Use commands')
        except StopIteration:
            #print('This was last contact')
            cprint('Останній контакт!', 'blue')
    return inner

@input_error
def add_contact(args):   
    global phone_book
    return phone_book.add_contact(args) if args else "Введіть Ім'я та данні як аргументи"
    

@input_error     
def change_contact(args):  
    record = phone_book.data.get(args[0]) 
    if args[0] not in phone_book.keys():  
        record.add_phone(args)  
        return f'{args[0]} added to contacts!'
    elif len(args) == 3:          
        for key, values in phone_book.items():            
            if key == args[0] and args[1] in str(values.phones):
                record.change_phone(Phone(args[1]), Phone(args[2]))
    else:
        return "Для зміни номеру контакта введіть введіть у наступній послідовності:\n Ім'я старий номер новий номер"

@input_error
def change_email(args):
    if args[0] not in phone_book.keys():
        return f'{args[0]} Такого контакту неіснуе!'
    record = phone_book.data.get(args[0])
    for key in phone_book.keys():            
        if key == args[0]:
            record.change_email_iner(Email(args[1]))
    # return f'Email was changed in Contact > {record}'

@input_error
def change_birthday(args): 
    if args[0] not in phone_book.keys():
        return f'{args[0]} Такого контакту неіснуе!'
    record = phone_book.data.get(args[0])
    for key in phone_book.keys():            
        if key == args[0]:
            record.change_birthday_in(Birthday(args[1]))
        return f'День народження змінено > {record}'

@input_error
def del_phone(args):
    return phone_book.del_phone(args) if args else "Введіть Ім'я та Телефон як аргументи"
    # record = phone_book.data.get(args[0])
    # for key in phone_book.keys():            
    #         if key == args[0]:
    #             record.delete_phone(args[1])
    #             return f'Phone {args[1]} was deleted from {key} contact!'

def search(args):
    global phone_book
    return phone_book.search_in(args) if args else "Введіть шаблон для пошуку як аргумент"

@input_error
def del_record(args):
    global phone_book
    return phone_book.delete_contact(args[0]) if args else "Введіть Ім'я як аргумент"

@input_error
def edit_contact(args):
    global phone_book
    return phone_book.edit_contact(args[0]) if args else "Введіть Ім'я як аргумент"

@input_error
def show():
    return next(phone_book.iterator())

@input_error
def birthday_in_days(args):
    global phone_book
    return phone_book.birthday_in_days(args) if args else "Введіть кількість днів як аргумент"

@input_error
def main():
    try:
        unpack_data()
    except Exception:
        global phone_book
        phone_book = AddressBook()

    print(show_help())
    session = PromptSession(auto_suggest=AutoSuggestFromHistory(), completer=IntentCompleter(commands))
    while True:
        b = session.prompt('Введіть потрібну вам команду > ').strip() 
        c = ['exit']
        d, *args = b.split(' ')
        with contextlib.suppress(ValueError):
            if int(d):
                for a, i in enumerate(commands, start=1):
                    if a == int(d):
                        d = i

        if b in c or d in c or d == '0':
            pack_data()
            cprint('See you soon!','green')
            break
        elif b == 'show_all' or d == 'show_all':
            print(phone_book.show_all_cont())
        # elif b == 'hello' or d == 'hello':
        #     print('How can i help you?')
        elif b == 'help' or d == 'help':
            print(show_help())
        elif b == 'next' or d == 'next':
            cprint(show(), 'green')
        elif d == 'birthday_in_days':
            cprint(birthday_in_days(args),'light_cyan' )
        elif b in commands:
            cprint('Enter arguments to command', 'red')
        elif d == 'add':
            cprint(add_contact(args), 'light_cyan')
        # elif d == 'change':
        #     cprint(change_contact(args), 'green')
        # elif d == 'change_email':
        #     cprint(change_email(args), 'green')
        # elif d == 'change_bd':
            # cprint(change_birthday(args), 'green')
        elif d == 'phones':
            cprint(phone_book.show_phones(args), 'light_cyan')
        elif d == 'del_phone':
            cprint(del_phone(args), 'light_cyan')
        elif d == 'search':
            cprint(search(args), 'light_cyan')
        elif d == 'del_contact':
            cprint(del_record(args), 'light_cyan')
        elif d == 'edit_contact':
            cprint(edit_contact(args), 'light_cyan')
        else:
            cprint('Please enter correct command. Use command "help" to see more.', 'red')


if __name__ == "__main__":
    main()