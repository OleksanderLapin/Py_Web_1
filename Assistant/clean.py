import sys
from pathlib import Path
import os
import shutil

#пошук файлів у вкладених папках
def search(path):    
#    print(os.getcwdb())
    list_dir_ = ['video', 'audio', 'documents', 'images', 'archives'] #перелік папок для работи скрипта (сервісні папки)
    list_dir = [path]
    all_dir = os.walk(path)
    count = 0
    for i in all_dir: #перебор папок           
        
        if i[0] == str(path):
            list_name_file = i[2]
            if list_name_file != []:
                for f in list_name_file:  
                    file= os.path.join(path, f)             
                    count = move_file(file, path, count) #виклик функції перенесення файлів                      
        else:            
            name_dir = i[0] #путь назва вкладеної папки
            one_dir = os.path.basename(name_dir) # назва вкладеної папики

            if one_dir in list_dir_: # перевірка чи папка є сервісною для роботи
                pass
            elif str(name_dir).find('archives') != -1:
                print(name_dir)
            else: # якщо ні то обробляємо
                #print(name_dir ,path + normalize(name_dir.split(path)[1]))
                os.rename(name_dir, path + normalize(name_dir.split(path)[1])) # переіменування папки в латиницю
                list_name_file = i[2]
                #print('додаємо папку до переліку',name_dir)
                list_dir.append(path + normalize(name_dir.split(path)[1]))    
                #print(list_dir)
                if list_name_file != []:
                    for f in list_name_file:   
                        file= os.path.join(name_dir, f)             
                        count = move_file(file, path, count) #виклик функції перенесення файлів         
                        ##move_file(fr'{name_dir}/{f}', path) #виклик функції перенесення файлів   
    #print('list_dir search', list_dir)      
    return path, list_dir, count

#переміщення файлів до папок та перевод назви файлу у латиницю
def move_file(path_file, path, count):
    #print(path_file)
    
    list_dir_ = ['video', 'audio', 'documents', 'images', 'archives'] #перелік папок для работи скрипта(сервісні папки)
    dict_dir = {'images':['JPEG', 'PNG', 'JPG', 'SVG'], 
                'video': ['AVI', 'MP4', 'MOV', 'MKV'], 
                'audio': ['MP3', 'OGG', 'WAV', 'AMR'], 
                'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'], 
                'archives': ['ZIP', 'GZ', 'TAR']} # словник з розширеннями файлів
    
    file = os.path.basename(path_file) #відокремлюємо назву файлу
    
    suffix_file = str(Path(path_file).suffix).upper()[1:] #приведення розширення до вигляду як у словнику
    file = normalize(file.split('.')[0]) + str(Path(path_file).suffix) #переіменування файла у латиницю

    #фільтруваня файла по групах

    for suffile in dict_dir.keys():
        
        if suffix_file in dict_dir[suffile]:
            
            if suffile != 'archives':
                folder = os.path.join(path, suffile, file)
                #print('folder ', folder)
                print('path_file ', path_file)
                os.rename(path_file, folder)
                count += 1
            elif suffile == 'archives':
                file = file.split('.')[0]
                folder = os.path.join(path,'archives', file)
                shutil.unpack_archive(path_file, folder)                
                print('path_file ', path_file)
                os.remove(path_file)    
                count += 1
            else:
                print('Невідомий файл -->', fr'{path_file}') 
    return count    

#Перевірка наявності папок для работи скрипта у вибраній дерікторії
def folder_project(path):
    list_dir_work = os.listdir(path) #отримання переліку папок та файлів у вибраній папці
    list_dir_ = ['video', 'audio', 'documents', 'images', 'archives'] #перелік папок для работи скрипта(сервісні папки)
    
    for i in list_dir_work: #перебираємо отриманий перелік
        folder = os.path.join(path, i)
        
        if os.path.isdir(folder): #перевіряємо чи то є папка 
            
            if i in list_dir_: #якщо так, то дивимось чи є ця папка в нашому робочому переліку
                #print(fr'this folder {i} exists')
                list_dir_.remove(i) #видаляємо існуючу папку з переліку папок для работи скрипта
    
    for d in list_dir_: #перебираєме перелік папок для работи скрипта щоб створити не існуючи папки 
        folder = os.path.join(path, d)
        os.mkdir(folder)
        #os.mkdir(fr'{path}/{d}') #створюємо папку
    #print('перевірив')
                
#Функція переводу з кирилиці у латиницю назв
def normalize(name):    
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ "
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g", "_")

    TRANS = {}

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()    

    return name.translate(TRANS)   

# Видалення пустих папок
def del_empty_dir(list_dir=[]):
    #print(list_dir)
    list_dir_ = ['video', 'audio', 'documents', 'images', 'archives'] #перелік папок для работи скрипта(сервісні папки)        
   
    if int(list_dir[0].find('/')) >= 0:
        delimiter = '/'
    else:
        delimiter = '\\'
   # print('delimiter', delimiter)

    for dir in sorted(list_dir, key=lambda x: len(x.split(delimiter)), reverse=True):    
        
        if dir in list_dir_: # перевірка чи входить папка у перелік сервісних папок
            pass
        else:    
            if os.listdir(dir) :                
                #print(os.listdir(dir), dir)
                if os.listdir(dir) == ['.DS_Store']:
                    #print('пустая + DS_Store', dir)
                    shutil.rmtree(dir)
            else:
                #print('пустая', dir)
                shutil.rmtree(dir)
                
def main():

    try :        
        #print(os.name)
        folder = input("Вветідть шлях до потрібнох папки > ")
        ##folder_project(sys.argv[1])
        folder_project(folder.strip())
        #search(sys.argv[1])
        ##del_empty_dir(search(sys.argv[1])[1]) 
        f = search(folder.strip())
        del_empty_dir(f[1])
        print(f"Відсортовано {f[2]} файл(ов/ів)")
        print("Сортування завершено")
    except Exception as er:
        print(er)
        print('Ну і де шлях на папки?')

if __name__ == '__main__':
    main()
