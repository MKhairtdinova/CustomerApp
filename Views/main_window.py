import tkinter as tk
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Views.open_window import OpenWindow
from ttkwidgets import *
import os
import tkinter.messagebox as msgb
from Views.analysis_settings import AnalysisSettings
from matplotlib.figure import Figure

# Главное окно приложения
class MainWindow:
    def __init__(self, master):
        self._master = master
        self._master.title('Customer Segmentation App')

        # поле отображения виджетов
        self._frame = tk.Frame(self._master)

        # главное меню (которое сверху)
        self._main_menu = Menu(self._frame)
        self._master.config(menu=self._main_menu)

        file_menu = Menu(self._main_menu, tearoff=0)
        file_menu.add_command(label='Открыть...', command=self.open_explore_window)
        file_menu.add_command(label='Выход', command=self._close)

        self._main_menu.add_cascade(label='Файл', menu=file_menu)

        self._dir_l = Label(self._frame, text='Текущая директория', anchor='e', width=25)
        self._dir = Label(self._frame, width=40, anchor='w')
        self._dir['text'] = 'Не выбрана'
        self._file = ''
        self._sep=''

        self._data_frame = LabelFrame(master=self._frame, text='Обзор данных')

        # Обзор признаков
        self._explorer = CheckboxTreeview(self._data_frame, height=20)    # дерево признаков
        self._explorer.heading('#0', text='Дерево данных')

        # Статистика по признакам
        self._stats_frame = LabelFrame(master=self._data_frame, text='Статистика по признакам', height=20)
        self._stat_feature = StringVar()
        self._headers_list = []  # список признаков в датасете
        self._headers_list.append('Нет признаков')
        self._stat_feature.set(self._headers_list[0])
        self._features_stat_lst = OptionMenu(self._stats_frame, self._stat_feature, *self._headers_list)
        self._features_stat_lst.config(width=20)

        self._stats_val_frame = Frame(self._stats_frame)

        # показатели по статистикам
        self._min_stat_l = Label(self._stats_val_frame)  # Минимальное значение
        self._max_stat_l = Label(self._stats_val_frame)  # Максимальное значение
        self._avg_stat_l = Label(self._stats_val_frame)  # Среднее арифметическое
        self._med_stat_l = Label(self._stats_val_frame)  # Медиана
        self._nul_stat_l = Label(self._stats_val_frame)  # Пустых значений
        self._all_stat_l = Label(self._stats_val_frame)  # Всего строк

        self._min_stat_val = Label(self._stats_val_frame, width=10)
        self._max_stat_val = Label(self._stats_val_frame, width=10)
        self._avg_stat_val = Label(self._stats_val_frame, width=10)
        self._med_stat_val = Label(self._stats_val_frame, width=10)
        self._nul_stat_val = Label(self._stats_val_frame, width=10)
        self._all_stat_val = Label(self._stats_val_frame, width=10)

        self._plot = Figure(figsize=(5, 4), dpi=100)
        self._canvas = FigureCanvasTkAgg(self._plot, master=self._stats_frame)
        self._canvas.draw()

        self._analysis = Button(self._frame, text='Выполнить анализ', command=self._analyse)

        # Упаковка в нужном виде
        self._dir_l.grid(row=0, column=0, columnspan=6, rowspan=2, sticky=E, ipadx=10, padx=5)
        self._dir.grid(row=0, column=7, columnspan=8, rowspan=2, sticky=N+S+W+E, padx=5)

        self._data_frame.grid(row=2, column=0, rowspan=12, columnspan=14, padx=10, sticky=N+S+W+E)

        self._explorer.grid(row=0, column=0, columnspan=4, rowspan=12, sticky=N+S+W+E, padx=5, pady=5)
        self._stats_frame.grid(row=0, column=6, columnspan=10, rowspan=12, sticky=N+S+W+E, padx=5, pady=3)

        self._features_stat_lst.pack()

        self._all_stat_l.grid(row=0, column=0, sticky=E)
        self._nul_stat_l.grid(row=1, column=0, sticky=E)
        self._min_stat_l.grid(row=2, column=0, sticky=E)
        self._max_stat_l.grid(row=3, column=0, sticky=E)
        self._avg_stat_l.grid(row=4, column=0, sticky=E)
        self._med_stat_l.grid(row=5, column=0, sticky=E)

        self._all_stat_val.grid(row=0, column=1, sticky=E)
        self._nul_stat_val.grid(row=1, column=1, sticky=E)
        self._min_stat_val.grid(row=2, column=1, sticky=E)
        self._max_stat_val.grid(row=3, column=1, sticky=E)
        self._avg_stat_val.grid(row=4, column=1, sticky=E)
        self._med_stat_val.grid(row=5, column=1, sticky=E)

        self._stats_val_frame.pack()

        self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self._frame.grid(row=0, column=0)
        self._analysis.grid(row=14, column=0, pady=10, columnspan=14)
        self._frame.grid(row=0, column=0)

        self._stats = dict()

    """Открытие окна настройки алгоритма анализа"""
    def _analyse(self):
        l = self._get_checked_features()

        if len(l) == 0:
            msgb.showerror(title='Нет данных',
                           message='Нельзя выполнить анализ, пока не загружен файл с данными и не выбраны поля для анализа')
        else:
            self.analysis_set = tk.Toplevel(self._master)
            self.app = AnalysisSettings(self.analysis_set, file_path=self._file, features_lst=l, separator=self._sep)
            self._master.withdraw()
            self._master.wait_window(self.analysis_set)
            self._master.deiconify()

    """Определение параметров которые выбрал пользователь для анализа"""
    def _get_checked_features(self):
        l = self._explorer.get_checked()

        features = []

        for i in l:
            features.append(self._explorer.item(i)['text'])

        return features

    """ Открытие окна для выбора файла-источника данных"""
    def open_explore_window(self):
        self._open_window = tk.Toplevel(self._master)
        self._open_app = OpenWindow(self._open_window)
        self._master.withdraw()
        self._master.wait_window(self._open_window)
        self._master.deiconify()

        if self._open_app.file_result.get() == 'OK':
            self._file = self._open_app.file_name.get()
            self._sep = self._open_app.sep.get()
            self._dir['text'] = self._file if self._file != '' else 'Не выбрана'


            self._headers = self._open_app.headers_list.get()

            if self._headers != '':
                self._headers_list = self._open_app.headers_list.get().split(';')

                menu = self._features_stat_lst["menu"]
                menu.delete(0, "end")
                for string in self._headers_list:
                    menu.add_command(label=string, command=lambda value=string: self._show_statistics(value))

                self._stat_feature.set(self._headers_list[0])

                self._stats = self._open_app.stats

                self.show_view()
                self._show_statistics(self._headers_list[0])
            else:
                self._headers_list = []

                menu = self._features_stat_lst["menu"]
                menu.delete(0, "end")
                menu.add_command(label='Нет признаков')

                self._stats = dict()

                self.show_view()
                self._headers_list.append('Нет признаков')
                self._clear_statistics()

            self._stat_feature.set(self._headers_list[0])

            del self._headers


        del self._open_window
        del self._open_app

    """ Отображение признаков из файла"""
    def show_view(self):
        file_name = os.path.basename(self._dir['text'])
        self._explorer.destroy()

        self._explorer = CheckboxTreeview(self._data_frame, height=20)

        folder = ''

        if len(self._headers_list) != 0:
            self._explorer.heading('#0', text='Дерево данных')

            folder = self._explorer.insert("", 1, '0', text=file_name)

        parsed_features = 0

        for feature in self._headers_list:
            parsed_features += 1
            self._explorer.insert(folder, "end", str(parsed_features), text=feature)

        self._explorer.grid(row=0, column=0, columnspan=5, rowspan=12, sticky=N+S+W+E, padx=5, pady=5)

    """Отображение статистик по выбранному параметру"""
    def _show_statistics(self, header):
        self._stat_feature.set(header)
        self._clear_statistics()

        for stat in self._stats[header]:

            if stat[0] != 'plt':
                if stat[0] == 'Всего':
                    self._all_stat_l['text'] = 'Всего'
                    self._all_stat_val['text'] = stat[1]

                if stat[0] == 'Пустых':
                    self._nul_stat_l['text'] = 'Пустых'
                    self._nul_stat_val['text'] = stat[1]

                if stat[0] == 'Max':
                    self._max_stat_l['text'] = 'Max'
                    self._max_stat_val['text'] = stat[1]

                if stat[0] == 'Min':
                    self._min_stat_l['text'] = 'Min'
                    self._min_stat_val['text'] = stat[1]

                if stat[0] == 'Ср. арифм.':
                    self._avg_stat_l['text'] = 'Ср. арифм.'
                    self._avg_stat_val['text'] = stat[1]

                if stat[0] == 'Медиана':
                    self._med_stat_l['text'] = 'Медиана'
                    self._med_stat_val['text'] = stat[1]
            else:
                self._canvas.get_tk_widget().destroy()
                self._plot = Figure(figsize=(5, 4), dpi=100)
                p = self._plot.gca()
                p.hist(stat[1].tolist())
                self._canvas = FigureCanvasTkAgg(self._plot, master=self._stats_frame)
                self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
                self._canvas.draw()

    """Очистка окна отображения статистики"""
    def _clear_statistics(self):
        self._all_stat_l['text'] = ''
        self._nul_stat_l['text'] = ''
        self._min_stat_l['text'] = ''
        self._max_stat_l['text'] = ''
        self._avg_stat_l['text'] = ''
        self._med_stat_l['text'] = ''

        self._all_stat_val['text'] = ''
        self._nul_stat_val['text'] = ''
        self._min_stat_val['text'] = ''
        self._max_stat_val['text'] = ''
        self._avg_stat_val['text'] = ''
        self._med_stat_val['text'] = ''

        self._canvas.get_tk_widget().destroy()
        self._plot = Figure(figsize=(5, 4), dpi=100)
        self._canvas = FigureCanvasTkAgg(self._plot, master=self._stats_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def _close(self):
        self._master.destroy()







