
from termcolor import colored, cprint
from prettytable import PrettyTable
import os
from Assistant import Phone_Book, notes, clean


def input_text():
    text = colored('Зробіть свій вибір > ', 'yellow')
    return input(text).lower().split(' ')
    
def show_greeting():      
     
    x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 

    x.field_names = [colored("Вас вітає бот помічник, наразі доступні наступні модулі:", 'light_blue')]
    x.add_row([colored("1. Сортування файлів","blue")])     
    x.add_row([colored("2. Робота з адресною книгою","blue")])
    x.add_row([colored("3. Робота з нотатками","blue")])
    x.add_row([colored("0. Закінчити роботу програми","blue")])

    print(x) # показуємо табличку

def run():    
    os.system('cls||clear')  # чистим консоль перед виводом
    
    sorting = False
    addresbook = False
    notes_local = False
    
    while True:
        
        if not (sorting or addresbook or notes_local):
            show_greeting()        
            answer = input_text()
        
            try:
                if int(answer[0]) == 0:
                    cprint("Good bye!", 'blue')
                    break
                if int(answer[0]) == 1:
                    sorting = True
                if int(answer[0]) == 2:
                    addresbook = True
                if int(answer[0]) == 3:
                    notes_local = True
            except ValueError as e:
                cprint('Введіть будь ласка число від 0 до 3', 'red')

        if sorting:  #  тут виклик логіки роботи з сортувальником        
            clean.main()
            sorting = False
            # os.system('cls||clear')  # чистим консоль
        
        if addresbook:  #  тут виклик логіки роботи з Phone_Book 
            Phone_Book.main()
            addresbook = False
            os.system('cls||clear')  # чистим консоль
            
        if notes_local: #  тут виклик логіки роботи з нотатками             
            notes.main()          
            notes_local = False
            os.system('cls||clear')  # чистим консоль

if __name__ == '__main__':
    run()