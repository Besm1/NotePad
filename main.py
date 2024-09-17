# from cProfile import label
# from ctypes import windll
# from os.path import exists
# from pty import master_open
from tkinter import *
from tkinter.filedialog import askopenfile, askopenfilename, asksaveasfile
from tkinter.messagebox import showinfo, askyesno, askyesnocancel
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Radiobutton
from os import path
# from unittest.mock import file_spec

import keyboard
from select import select


class Notepad:


    def __init__(self):
        self.root = Tk()
        self.root.geometry('600x400')
        self.root.resizable(True, True)
        self.root.minsize(width=260, height=220)
        self.root.title('BS_Notepad')

        self.file_spec = ''     # полный путь к файлу
        self.file_name = ''     # имя файла

        self.seek_direction = 0     # Направление поиска

        self.root.option_add('*tearOff', FALSE)   # глобальная установка параметра для меню

        self.file_menu = Menu()
        set_cascade(self.file_menu, 'Создать'
                         , ('Открыть...', self.open_file)
                         , ('Сохранить', self.save_existing_file)
                         , ("Сохранить как...", self.save_file_as)
                         , '__sep__'
                         , ('Выход', self.on_exit))

        # self.edit_menu = Menu()
        # set_cascade(self.edit_menu, 'Отменить    CTRL/Z'
        #                  , 'Вырезать    CTRL/X'
        #                  , 'Копировать  CTRL/C'
        #                  , 'Вставить    CTRL/V'
        #                  , 'Удалить'
        #                  , '__sep__'
        #                  , 'Заменить...  CTRL/H'
        #                  , 'Перейти...   CTRL/G'
        #                  , '__sep__'
        #                  , 'Найти...     CTRL/F'
        #                  , 'Найти далее  F3'
        #                  )

        self.help_menu = Menu()
        set_cascade(self.help_menu, ('Помощь пользователю', self.show_help)
                         , ('О программе', self.show_about))

        self.test_menu = Menu()
        set_cascade(self.test_menu, ('Флаг editor.modified', self.test_modified)
                    , ('test askyesnocancel', self.test_askyesnocancel))

        self.main_menu = Menu()
        set_cascade(self.main_menu, ('__cascade__', "Файл", self.file_menu)
                         # , ('__cascade__', "Правка", self.edit_menu)
                         , ('__cascade__', "Справка", self.help_menu)
                         , ('__cascade__', "Тест", self.test_menu)
                         )


        self.root.config(menu=self.main_menu)

        self.editor = ScrolledText(master=self.root)
        self.editor.pack(fill=BOTH, expand=1)

        self.root.protocol("WM_DELETE_WINDOW",  self.on_exit)

        self.editor.bind('<Control-f>', self.find)
        self.find_test = ''

        self.root.mainloop()

    def find(self, event):
        self.editor.tag_remove('found', '1.0', END)
        ask_find = Window(title='Поиск', geometry='300x200')
        s = Entry(master=ask_find)
        Label(master=ask_find, text='Найти:').place(x=10, y=10)
        text_to_find = Entry(master=ask_find, width=38)
        text_to_find.place(x=55, y=10)
        text_to_find.focus_set()

        frame_seek_direction = Frame(master=ask_find, borderwidth=1, relief=SOLID, padding=[8, 10])

        self.seek_direction = StringVar(master=frame_seek_direction, value='1')
        position = {"padx": 6, "pady": 6, "anchor": NW}

        Label(master=frame_seek_direction, text='направление:').grid(row=1, column=0)
        rbtn_forward = Radiobutton(master=frame_seek_direction, text='вниз', value='1', variable=self.seek_direction)
        rbtn_forward.grid(row=1, column=1)
        rbtn_backward = Radiobutton(master=frame_seek_direction, text='вверх', value='-1', variable=self.seek_direction)
        rbtn_backward.grid(row=2, column=1)

        btn_find = Button(master=frame_seek_direction, text='Поиск', command=self.do_seek)
        btn_find.grid(row = 3, column=1)

        lbl=Label(master=frame_seek_direction, textvariable=self.seek_direction)
        lbl.grid(row=4, column=0)
        Label(master=frame_seek_direction, text=lbl['text']).grid(row=4, column=1)


        frame_seek_direction.place(x=130, y=55)



        # Label(master=ask_find, text='Заменить:').pack(side=LEFT)
        # text_to_replace = Entry(master=ask_find)
        # text_to_replace.pack(side=LEFT, fill=BOTH,expand=1)
        #

    def do_seek(self):

        print(self.seek_direction.get())

    def on_exit(self):
        if self.editor.edit_modified():
            answ = askyesnocancel(title='Файл не сохранён', message=f'Файл не сохранён. Хотите его сохранить?')
            if answ is None:
                return
            elif answ:
                self.save_file(self.file_spec)
        self.root.destroy()


    def test_modified(self):
        print(self.editor.edit_modified())

    def test_askyesnocancel(self):
        print(askyesnocancel(title='Файл не сохранён', message=f'Файл не сохранён. Хотите его сохранить?'))

    def f_name_changed(self):
        self.file_name = self.file_spec[self.file_spec.rfind('/')+1:]
        self.root.title('NotePad - ' + self.file_name)

    def save_existing_file(self):
        self.save_file(self.file_spec)

    def save_file_as(self):
        self.save_file('')

    def save_file(self, filespec):
        if filespec is None or filespec == '':
            file = asksaveasfile(filetypes=[('Текстовые файлы', '.txt'), ('Любые файлы', '.*')], defaultextension='.txt',title='Запись файла')
            if file is None:
                return
            file.write(self.editor.get('1.0', END))
            file.close()
            self.file_spec = file.name
            self.f_name_changed()
        else:
            with open(filespec, mode='w') as file:
                file.write(self.editor.get('1.0', END))
        self.editor.edit_modified(False)

    def open_file(self):
        if self.editor.edit_modified():
             answer = askyesnocancel(title='Файл не сохранён', message=f'Файл не сохранён. Хотите его сохранить?')
             if answer is None:
                 return
             elif answer:
                 self.save_file(self.file_spec)
        else:
            self.editor.delete('1.0', END)
        self.file_spec = askopenfilename(initialdir='/', filetypes=(('Текстовые файлы', '.txt'), ('Все файлы', '*')))
        if self.file_spec is None:
            return
        with open(self.file_spec, encoding='utf-8') as file:
            self.editor.insert('1.0', chars=file.read())
        self.f_name_changed()
        self.editor.edit_modified(False)

    def show_about(self):
        showinfo('О программе', 'Программа NotePad\nАвтор - Смирнов Б.Е.\nВерсия 1.0, сборка 16.09.2024')

    def show_help(self):
        w_help = Window(geometry='300x250')
        help = Label(master=w_help, text='''
Программа BS_Notepad является аналогом
программы NotePad.

В основном окне есть меню, при помощи
которого можно открывать/сохранять файлы,
редактировать текст и получать помощь.
 
Программа поставляется в виде "как есть".
Вы её используете на свой риск, автор не
несёт никакой ответственности за причинённый
Вам вред от её использования.
 
Если она Вам не нравится, то это Ваше личное
дело, и никаких претензий автор не принимает. 
        ''')
        help.pack(fill=BOTH, expand=1)




class Window(Tk):

    windows_count = 0

    def __init__(self, title='Window_', geometry='800x600', resizable = (False, False)):
        super().__init__()

        self.windows_count += 1

        self.title(title + (str(self.windows_count) if title == 'Window_' else ''))
        # print(self.title)
        self.geometry(geometry)
        self.resizable(*resizable)

def set_cascade(menu: Menu, *commands):
    for c_ in commands:
        if isinstance(c_, tuple) and len(c_) == 3:
            spec, name, option = c_
        elif isinstance(c_, tuple) and len(c_) == 2:
            spec, name = c_
            option = None
        else:
            spec, name, option = c_, None, None
        if spec == '__sep__':
            menu.add_separator()
        elif spec == '__cascade__':
            menu.add_cascade(label=name, menu=option)
        elif isinstance(spec, str):
            menu.add_command(label=spec, command=name)
        else:
            pass


if __name__ == '__main__':
    np = Notepad()
