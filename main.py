# from cProfile import label
# from ctypes import windll
# from os.path import exists
# from pty import master_open
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.messagebox import showinfo, askyesnocancel
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Radiobutton
from os import path
from winreg import DeleteKey

from keyboard import send
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

        self.search_direction = True     # Направление поиска - вперёд

        self.root.option_add('*tearOff', FALSE)   # глобальная установка параметра для меню

        self.file_menu = Menu()
        set_cascade(self.file_menu, 'Создать'
                         , ('Открыть...', self.open_file)
                         , ('Сохранить', self.save_existing_file)
                         , ("Сохранить как...", self.save_file_as)
                         , '__sep__'
                         , ('Выход', self.on_exit))

        self.edit_menu = Menu()
        set_cascade(self.edit_menu
                        , ('Отменить    CTRL/Z', self.undo)
                        , ('Повторить   CTRL/Y', self.redo)
                        , ('Вырезать    CTRL/X', self.cut)
                        , ('Копировать  CTRL/C', self.copy)
                        , ('Вставить    CTRL/V', self.paste)
                        , ('Удалить       DEL', self.delete)
                        , '__sep__'
        #                , ('Заменить...  CTRL/H', self.replace_dialog)
                        , ('Перейти...   CTRL/G', self.goto_dialog)
                        , '__sep__'
                        , ('Найти...     CTRL/F', self.find_dialog)
                        , ('Найти далее  F3', self.next_search)
                    )

        self.help_menu = Menu()
        set_cascade(self.help_menu, ('Помощь пользователю', self.show_help)
                         , ('О программе', self.show_about))

        self.main_menu = Menu()
        set_cascade(self.main_menu, ('__cascade__', "Файл", self.file_menu)
                         , ('__cascade__', "Правка", self.edit_menu)
                         , ('__cascade__', "Справка", self.help_menu)
                         )

        self.root.config(menu=self.main_menu)

        self.editor = ScrolledText(master=self.root, undo=True)
        self.editor.pack(fill=BOTH, expand=1)

        self.root.protocol("WM_DELETE_WINDOW",  self.on_exit)

        # self.editor.bind('<Control-f>', self.find_dialog)
        # self.editor.bind('<Control-F>', self.find_dialog)
        # #self.editor.bind('<Control-а>', self.find_dialog)
        # #self.editor.bind('<Control-А>', self.find_dialog)
        # self.editor.bind('<Control-G>', self.goto_dialog)
        # self.editor.bind('<Control-g>', self.goto_dialog)

        self.editor.bind('<F3>', self.next_search)
        self.editor.bind('<Shift-F3>', self.next_search)
        self.editor.bind('<Control-KeyPress>', self.ctrl_key)

        self.find_text = ''

        self.root.mainloop()

    def ctrl_key(self, event):
        if event.keycode==86:
            event.widget.event_generate("<<Paste>>")
        elif event.keycode==67:
            event.widget.event_generate("<<Copy>>")
        elif event.keycode==88:
            event.widget.event_generate("<<Cut>>")
        elif event.keycode==71: # Ctrl-G
            self.goto_dialog()
        elif event.keycode==70:
            self.find_dialog()


    def next_search(self, *event):
        self.search_direction = not (event[0].state & 0x01)  # 1 - Shift
        if self.find_text:
            # self.find_next()
            self.do_search()
        else:
            self.find_dialog(None)

    def find_dialog(self, *event):
        # Вызывается при нажатии CTRL/F
        self.editor.tag_remove('found', '1.0', END)
        self.ask_find = Toplevel()
        self.ask_find.title('Поиск')
        self.ask_find.geometry('300x150')
        self.ask_find.grab_set()
        self.ask_find.protocol("WM_DELETE_WINDOW", lambda: close_window(self.ask_find))  # перехватываем нажатие на крестик

        s = Entry(master=self.ask_find)
        Label(master=self.ask_find, text='Найти:').place(x=10, y=10)
        self.text_to_find = Entry(master=self.ask_find, width=38)
        if self.find_text:
            self.text_to_find.insert(0, self.find_text )
        self.text_to_find.place(x=55, y=10)
        self.text_to_find.focus_set()

        frame_search_direction = Frame(master=self.ask_find, borderwidth=1, relief=SOLID, padding=[8, 10])

        self.search_direction_var = BooleanVar(master=frame_search_direction, value=self.search_direction)
        position = {"padx": 6, "pady": 6, "anchor": NW}

        Label(master=frame_search_direction, text='направление:').grid(row=1, column=0)
        rbtn_forward = Radiobutton(master=frame_search_direction, text='вниз', value=True, variable=self.search_direction_var)
        rbtn_forward.grid(row=1, column=1)
        rbtn_backward = Radiobutton(master=frame_search_direction, text='вверх', value=False, variable=self.search_direction_var)
        rbtn_backward.grid(row=2, column=1)

        btn_find = Button(master=self.ask_find, text='Поиск', command=self.do_search_text)
        btn_find.place(x=20, y=55)
        self.text_to_find.bind(sequence='<Return>', func=self.do_search_text)

        frame_search_direction.place(x=130, y=55)

    def do_search_text(self, *event):
        # Вызывается при нажатии на кнопку "Поиск" в диалоге "Поиск..." и при нажатии клавиши Return (через метод
        # do_search_text_2. Устанавливает параметры поиска и вызывает функцию непосредственного поиска.
        self.find_text = self.text_to_find.get()
        self.search_direction = self.search_direction_var.get()
        self.do_search()

    def do_search(self):
        # Функция непосредственного поиска текста self.find_text в self.editor.search в направлении
        #  self.search_direction от текущей позиции
        try:
            idx_1st_forwards = self.editor.index('found.last')
            idx_lst_backwards = self.editor.index('found.first')
            self.editor.tag_remove('found', idx_lst_backwards, idx_1st_forwards)
            self.editor.tag_remove('sel', idx_lst_backwards, idx_1st_forwards)
        except TclError:
            idx_1st_forwards = self.editor.index('insert')
            idx_lst_backwards = self.editor.index('insert')
        if self.search_direction: # Вниз
            idx = self.editor.search(pattern=self.find_text,index=idx_1st_forwards,stopindex=END
                               ,forwards=True)
        else:     # Вверх
            idx = self.editor.search(pattern=self.find_text, index=idx_lst_backwards, stopindex='1.0'
                                     ,backwards=True)
            # idx = self.editor.search(pattern=self.find_text, index='1.0', stopindex=self.editor.index('current')
            #                          ,backwards=True)
        if idx: # Нашли текст
            # self.editor.mark_set('current', index=idx)
            self.editor.mark_set('insert', index=idx)
            self.editor.see('insert')
            self.editor.tag_add('found', idx, idx + f' + {len(self.find_text)}c')
            self.editor.tag_add('sel', idx, idx + f' + {len(self.find_text)}c')
            self.editor.tag_config('found', background='blue', foreground='white')
            # self.editor.focus_set()
            # self.ask_find.destroy()
        else:
            showinfo('Поиск...', 'Искомый текст не найден')

    def goto_dialog(self, *event):
        # Вызывается при нажатии CTRL/F
        self.ask_goto = Toplevel()
        self.ask_goto.title('Переход на строку')
        self.ask_goto.geometry('200x90')
        self.ask_goto.grab_set()
        self.ask_goto.protocol("WM_DELETE_WINDOW", lambda: close_window(self.ask_goto))  # перехватываем нажатие на крестик

        # s = Entry(master=self.ask_goto, validate='key', validatecommand=(self.validate_decimal('%S')))
        Label(master=self.ask_goto, text='Номер строки:').place(x=10, y=10)
        reg = self.ask_goto.register(validate_decimal)
        self.line_to_go_fld = Entry(master=self.ask_goto, width=5, validate='key'
                                  , validatecommand=(reg, '%P'))
        self.line_to_go_fld.place(x=105, y=10)
        self.line_to_go_fld.focus_set()

        btn_goto = Button(master=self.ask_goto, text='Перейти', command=self.do_goto)
        btn_goto.place(x=10, y=45)
        self.line_to_go_fld.bind(sequence='<Return>', func=self.do_goto)


    def do_goto(self, *event):
        line_no = self.editor.index(END).split('.')[0]
        if int(self.line_to_go_fld.get()) > int(line_no) - 1:
            showinfo(title='BS_NotePad - Переход на строку', message='Номер строки превышает количество строк')
        else:
            self.editor.mark_set('insert', index=self.line_to_go_fld.get() + '.0')
            self.editor.see('insert')
            self.editor.focus_set()
            self.ask_goto.destroy()

    def copy(self):
        # send('ctrl+c')
        self.editor.event_generate('<<Copy>>')

    def paste(self):
        # send('ctrl+v')
        self.editor.event_generate('<<Paste>>')

    def cut(self):
        # send('ctrl+x')
        self.editor.event_generate('<<Cut>>')

    def undo(self):
        self.editor.edit_undo()

    def redo(self):
        self.editor.edit_redo()

    def delete(self):
        send('del')


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
        self.root.title('NotePad - ' + self.file_name)

    def save_existing_file(self):
        self.save_file(self.file_spec)

    def save_file_as(self):
        self.save_file('')

    def save_file(self, filespec):
        if filespec is None or filespec == '':
            file = asksaveasfile(filetypes=[('Текстовые файлы', '.txt'), ('Любые файлы', '.*')], defaultextension='.txt'
                                 ,title='Запись файла')
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
        # with open(self.file_spec, encoding='utf-8') as file:
        with open(self.file_spec) as file:
            self.editor.insert('1.0', chars=file.read())
            self.file_name = path.basename(self.file_spec)
        self.f_name_changed()
        self.editor.edit_modified(False)
        self.editor.mark_set('insert', '1.0')
        self.editor.see('1.0')
        self.editor.focus_set()

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

def close_window(window):
    window.grab_release()
    window.destroy()

def validate_decimal(key):
    return key.isdecimal()


if __name__ == '__main__':
    np = Notepad()
