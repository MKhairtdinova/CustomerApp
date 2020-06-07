import tkinter as tk
from tkinter import *
from tkinter import filedialog as fd
from tkmagicgrid import *
import csv
import io
from tkscrolledframe import ScrolledFrame
from Core.stats import Statistics

# Окно выбора файла-источника данных с определением разделителя csv
class OpenWindow(tk.Frame):

    def __init__(self, master):
        self._master = master
        self._master.bind('<Destroy>', lambda *args: self._close())

        x = self._master.winfo_screenwidth()  # размер  по горизонтали
        y = self._master.winfo_screenheight()

        self._master.title('Открыть CSV')

        self._frame = tk.Frame(self._master)

        self._main_menu = Menu(self._frame)
        self._master.config(menu=self._main_menu)

        self._settings_frame = Frame(self._frame)

        self._open_button = Button(self._settings_frame, text='Обзор...', command=self._open_csv_file)
        self._file_path = Label(self._settings_frame, width=50, anchor='w')

        self._sep_list = dict()
        self._sep_list['Запятая (,)'] = ','
        self._sep_list[r'Знак табуляции (\t)'] = '\t'
        self._sep_list['Точка с запятой (;)'] = ';'
        self._sep_list['Пробел'] = ' '
        self._sep_list['Точка (.)'] = '.'

        self._sep_var = StringVar(self._frame)
        self._sep_var.set('Запятая (,)')
        self._sep_var.trace_add('write', lambda *args: self._change_sep())

        self.sep = StringVar()
        self.sep.set(self._sep_list[str(self._sep_var.get())])
        self.file_name = StringVar()
        self.file_name.set('')
        self.file_result = StringVar()
        self.file_result.set('')

        self._separator_lst = OptionMenu(self._settings_frame, self._sep_var, *(self._sep_list.keys()))

        self._sep_label = Label(self._settings_frame, text='Разделитель значений', width=50, anchor='e')

        self._preview = ScrolledFrame(self._frame, width=x / 2, height=y / 2, bg='gray', bd=5)
        self._preview.bind_arrow_keys(self._frame)
        self._preview.bind_scroll_wheel(self._frame)
        self._inner_frame = self._preview.display_widget(Frame)
        self._grid = MagicGrid(self._inner_frame)
        self._save = Button(self._frame, text="Ok", command=self._save_file)

        self._settings_frame.pack()

        self._open_button.grid(row=0, column=0, sticky=E, padx=10, pady=5)
        self._file_path.grid(row=0, column=1, sticky=W)
        self._sep_label.grid(row=1, column=0, sticky=E, pady=5)
        self._separator_lst.grid(row=1, column=1, sticky=W)

        self._frame.grid(row=0, column=0)

        self._preview.pack()
        self._grid.pack(side="top", expand=1, fill="both")
        self._save.pack()
        self.headers_list = StringVar()
        self.headers_list.set('')

        self.stats = dict()

    """ При закрытии \"крестиком\""""
    def _close(self):
        self.file_name.set('')
        self.file_result.set('Cancel')

    """ Изменение разделителя в csv-файле """
    def _change_sep(self):
        self.sep.set(self._sep_list[str(self._sep_var.get())])

        if self.file_name.get() != '':
            self._show_grid()

    """ Отображение данных файла в таблице (первые 20 записей)"""
    def _show_grid(self):
        # destroy ломает переменные, поэтому сохраним их
        file_save = self.file_name.get()
        sep_save = self.sep.get()
        headers_save = self.headers_list.get()

        self._grid.destroy()

        self.sep.set(sep_save)
        self.file_name.set(file_save)
        self.headers_list.set(headers_save)

        self._grid = MagicGrid(self._inner_frame)
        self._grid.pack(side="top", expand=1, fill="both")

        if self.file_name.get() != '':
            with io.open(self.file_name.get(), "r", newline="") as csv_file:
                reader = csv.reader(csv_file, delimiter=self.sep.get())
                parsed_rows = 0
                for row in reader:
                    if parsed_rows == 0:
                        # Первая строка как заголовок + сохраним для отображения в главном окне
                        self._grid.add_header(*row)
                        self.headers_list.set(";".join(row))
                    else:
                        self._grid.add_row(*row)
                    parsed_rows += 1

                    if parsed_rows == 20:
                        break

    """ Открытие csv-файла"""
    def _open_csv_file(self):
        self.file_name.set(fd.askopenfilename(filetypes=[("CSV-файл", ".csv")]))
        self._file_path['text'] = self.file_name.get()

        self._show_grid()

    """Закрытие при помощи кнопки "OK", чтобы сохранить данные о файле"""
    def _save_file(self):
        # destroy ломает переменные, поэтому сохраним их
        file_save = self.file_name.get()
        sep_save = self.sep.get()
        headers_save = self.headers_list.get()

        self._master.destroy()

        self.sep.set(sep_save)
        self.file_name.set(file_save)
        self.headers_list.set(headers_save)

        # если есть данные, то сохранить статистику
        if self.file_name.get() != '':
            self.stats = Statistics.get_df_statistics(self.file_name.get(), self.sep.get())

        self.file_result.set('OK')



    # Для отладки
    def __repr__(self):
        val = 'file_path = ' + self.file_name.get() \
              + '\n' + 'sep = ' + self.sep.get() \
              + '\n' + 'headers: ' + self.headers_list.get().split(';')
        return val
