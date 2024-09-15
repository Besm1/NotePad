from cProfile import label
from tkinter import *
import keyboard

class Notepad():


    def __init__(self):
        self.window = Tk()
        self.window.geometry('260x220')
        self.window.resizable(True, True)
        self.window.minsize(width=260, height=220)

        self.window.option_add('*tearOff', FALSE)   # глобальная установка параметра для меню

        self.file_menu = Menu()
        self.file_menu.add_command(label='Создать')
        self.file_menu.add_command(label='Открыть...')
        self.file_menu.add_command(label='Сохранить')
        self.file_menu.add_command(label='Сохранить как...')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Выход', command=self.cmd_edit)

        self.edit_menu = Menu()
        self.edit_menu.add_command(label='Отменить    CTRL/Z')
        self.edit_menu.add_command(label='Вырезать    CTRL/X')
        self.edit_menu.add_command(label='Копировать  CTRL/C')
        self.edit_menu.add_command(label='Вставить    CTRL/V')
        self.edit_menu.add_command(label='Удалить')
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Заменить...  CTRL/H')
        self.edit_menu.add_command(label='Перейти...   CTRL/G')
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Найти...     CTRL/F')
        self.edit_menu.add_command(label='Найти далее  F3')

        self.help_menu = Menu()
        self.help_menu.add_command(label='Помощь пользователю...')
        self.help_menu.add_command(label='О программе')

        self.main_menu = Menu()
        self.main_menu.add_cascade(label="Файл", menu=self.file_menu)
        self.main_menu.add_cascade(label="Правка", menu=self.edit_menu)
        self.main_menu.add_cascade(label="Справка", menu=self.help_menu)

        self.window.config(menu=self.main_menu)

        self.window.bind('<Destroy>', self.w_destroy)

        self.window.mainloop()


    def w_destroy(self, event):
        print(f'Размеры окна: {(self.window.winfo_width(), self.window.winfo_height())}')

    def cmd_edit(self):
        self.window.destroy()

if __name__ == '__main__':
    np = Notepad()