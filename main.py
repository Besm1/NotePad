from cProfile import label
from ctypes import windll
from tkinter import *
from tkinter.messagebox import showinfo, askyesno
from tkinter.scrolledtext import ScrolledText

import keyboard

class Notepad():


    def __init__(self):
        self.root = Tk()
        self.root.geometry('260x220')
        self.root.resizable(True, True)
        self.root.minsize(width=260, height=220)
        self.root.title('BS_Notepad')

        self.root.option_add('*tearOff', FALSE)   # глобальная установка параметра для меню

        self.file_menu = Menu()
        self.set_cascade(self.file_menu, 'Создать', 'Открыть...', 'Сохранить', "Сохранить как..."
                         , '__sep__', ('Выход', self.cmd_exit))

        self.edit_menu = Menu()
        self.set_cascade(self.edit_menu, 'Отменить    CTRL/Z'
                         , 'Вырезать    CTRL/X'
                         , 'Копировать  CTRL/C'
                         , 'Вставить    CTRL/V'
                         , 'Удалить'
                         , '___sep__'
                         , 'Заменить...  CTRL/H'
                         , 'Перейти...   CTRL/G'
                         , '__sep__'
                         , 'Найти...     CTRL/F'
                         , 'Найти далее  F3'
                         )

        self.help_menu = Menu()
        self.set_cascade(self.help_menu, ('Помощь пользователю', self.show_help)
                         , ('О программе', self.show_about))

        self.main_menu = Menu()
        self.set_cascade(self.main_menu, ('__cascade__', "Файл", self.file_menu)
                         , ('__cascade__', "Правка", self.edit_menu)
                         , ('__cascade__', "Справка", self.help_menu)
                         )

        self.root.config(menu=self.main_menu)

        editor = ScrolledText(master=self.root)
        editor.pack(fill=BOTH, expand=1)

        # self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_exit)

        self.root.mainloop()


    def set_cascade(self, menu: Menu, *commands):
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


    def show_about(self):
        showinfo('О программе', 'Программа NotePad\nАвтор - Смирнов Б.Е.\nВерсия 1.0, сборка 16.09.2024')

    def cmd_exit(self):
        if not askyesno(title='Внимание!', message='Вы сохранили текст?'):
            showinfo(title='Ох, как печально!!', message='Шеф, всё пропало!!!')
        self.root.destroy()

    # def on_exit(self, wnd):



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

    def __init__(self, title='Window', geometry='800x600', resizable = (False, False)):
        super().__init__()

        self.windows_count += 1

        self.title = title + (str(self.windows_count) if title == 'Window_' else '')
        self.geometry(geometry)
        self.resizable(*resizable)


if __name__ == '__main__':
    np = Notepad()
