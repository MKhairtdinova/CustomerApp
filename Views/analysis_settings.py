import tkinter as tk
from tkinter import *
from tkinter import ttk
from Core import observer
from Views.Widgets import tk_int_entry as inte
import tkinter.messagebox as msgb
from Core import analyser
from Views import result_observer
from Views import progress


# Окно выбора алгоритма для анализа
class AnalysisSettings(tk.Frame):
    def __init__(self, master, file_path, features_lst, separator):
        self._file = file_path,
        self._features = features_lst
        self._sep = separator

        self._master = master

        self._master.title('Настройка алгоритма анализа')
        self._frame = tk.Frame(self._master)

        self._alg_frame = Frame(self._frame)

        # Список алгоритмов
        self._alg_lab = Label(self._alg_frame, text='Алгоритм')
        self._alg_dict = observer.Observer.get_algs_list()
        cur_alg_list = list(self._alg_dict.keys())

        self._alg_var = StringVar()
        self._alg_var.trace_add('write', lambda *args: self._change_alg_params())

        # Часть ввода параметров алгоритма
        self._alg_container = tk.Frame(self._alg_frame)
        self._alg_params_frame = tk.Frame(self._alg_container)  # контейнер с полями ввода (очищается при смене)
        self._alg_params_entries = dict()  # список виджетов ввода
        self._alg_params_values = dict()  # список значений полей ввода
        self._alg_help_values = dict()  # список вспомогательных (временных значений)
        self._alg_params_labels = dict()  # список подписей к полям ввода
        self._alg_label = None  # подпись к контейнеру параметров

        if len(cur_alg_list) != 0:
            self._alg_var.set(cur_alg_list[0])
        else:
            self._alg_var.set('Нет доступных алгоритмов')

        self._alg_lst = OptionMenu(self._alg_frame, self._alg_var,
                                   *cur_alg_list)

        # Список функций качества
        self._func_frame = Frame(self._frame)
        self._func_lab = Label(self._func_frame, text='Функция качества')
        self._func_var = StringVar()
        self._func_dict = observer.Observer.get_qf_list()
        self._func_var.trace_add('write', lambda *args: self._change_qf_params())

        cur_qf_lst = list(self._func_dict.keys())

        # Часть ввода параметров функции
        self._qf_container = tk.Frame(self._func_frame)
        self._qf_params_frame = tk.Frame(self._qf_container)  # контейнер с полями ввода (очищается при смене QF)
        self._qf_params_entries = dict()  # список виджетов ввода
        self._qf_params_values = dict()  # список значений полей ввода (будет передаваться в core)
        self._qf_help_values = dict()  # список вспомогательных значений
        self._qf_params_labels = dict()  # список подписей для полей ввода
        self._qf_label = None  # подпись к контейнеру параметров

        if len(cur_qf_lst) != 0:
            self._func_var.set(cur_qf_lst[0])
        else:
            self._func_var.set('Нет доступных функций качества')

        self._func_lst = OptionMenu(self._func_frame, self._func_var, *cur_qf_lst)

        self._num_lab = Label(self._frame, text='Максимальное количество признаков')
        self._num_value = StringVar()
        self._num_value.set('3')
        self._num_entry = inte.Lotfi(master=self._frame, textvar=self._num_value, restrict_type=int)
        self._num_entry.config(width=20)

        self._process = Button(self._frame, text='Найти подгруппы', command=self._analyse_data)

        self._alg_lab.grid(row=0, column=0, sticky=E, padx=3, pady=5)
        self._alg_lst.grid(row=0, column=1, sticky=W, padx=3, pady=5)
        self._alg_container.grid(row=1, column=0, columnspan=2, sticky=N+S+W+E, padx=3)
        self._alg_frame.grid(row=0, column=0, columnspan=2)

        self._sepa1 = ttk.Separator(self._frame, orient = tk.HORIZONTAL)
        self._sepa1.grid(row=1, column=0, columnspan=2, sticky=EW, padx=20)

        self._func_lab.grid(row=0, column=0, padx=3, pady=5)
        self._func_lst.grid(row=0, column=1, padx=3, pady=5)
        self._qf_container.grid(row=1, column=0, columnspan=2, sticky=N+S+W+E, padx=3)
        self._func_frame.grid(row=2, column=0, columnspan=2)

        self._sepa2 = ttk.Separator(self._frame, orient=tk.HORIZONTAL)
        self._sepa2.grid(row=3, column=0, columnspan=2, sticky=EW, padx=20)

        self._num_lab.grid(row=4, column=0, padx=3, pady=5)
        self._num_entry.grid(row=4, column=1, padx=3, pady=5)

        self._process.grid(row=5, column=0, columnspan=2, padx=3, pady=5)

        self._frame.pack()

    '''При изменении алгоритма необходимо пометять отображение параметров'''
    def _change_alg_params(self):
        # Удалим текущие параметры
        # Поскольку destroy удалит все имеющиеся сохраненные переменные, то нужно будет их перезаписать

        self._alg_params_frame.destroy()
        self._alg_params_frame = Frame(self._alg_container)

        self._alg_params_entries = dict()
        self._alg_params_values = dict()
        self._alg_help_values = dict()
        self._alg_params_labels = dict()

        if self._alg_var != 'Добавить свой алгоритм...':
            # Если алгоритм принимает какие-то параметры, кроме self, то необходимо отобразить формы их ввода
            param_lst = self._alg_dict[self._alg_var.get()][1]
            if len(param_lst) > 1:
                self._show_entries(params=param_lst,
                                   params_frame=self._alg_params_frame,
                                   frame_text='Параметры алгоритма поиска подгрупп',
                                   params_labels=self._alg_params_labels,
                                   params_values=self._alg_params_values,
                                   params_entries=self._alg_params_entries,
                                   help_values=self._alg_help_values,
                                   label=self._alg_label)

                self._alg_params_frame.pack()

    '''При изменении функции качества необходимо изменить отображение параметров'''
    def _change_qf_params(self):
        """Обработка изменения выбранной функции качества:
        нужно показать виджеты для ввода или открыть окно выбора исходного кода"""

        # Удалим текущие параметры
        # Поскольку destroy удалит все имеющиеся сохраненные переменные, то нужно будет их перезаписать

        self._qf_params_frame.destroy()
        self._qf_params_frame = Frame(self._qf_container)

        self._qf_params_entries = dict()
        self._qf_params_values = dict()
        self._qf_help_values = dict()
        self._qf_params_labels = dict()

        if self._func_var != 'Добавить свою функцию качества...':
            # Если функция принимает какие-то параметры, кроме self, то необходимо отобразить формы их ввода
            param_lst = self._func_dict[self._func_var.get()][1]
            if len(param_lst) > 1:
                self._show_entries(params=param_lst,
                                   params_frame=self._qf_params_frame,
                                   frame_text='Параметры функции качества',
                                   params_labels=self._qf_params_labels,
                                   params_values=self._qf_params_values,
                                   params_entries=self._qf_params_entries,
                                   help_values=self._qf_help_values,
                                   label=self._qf_label)

                self._qf_params_frame.pack()

    '''
    Отображение полей ввода для параметров
    params - параметры
    params_frame - контейнер для полей ввода 
    frame_text - подпись контейнера (параметры алгоритма или функции качества)
    param_labels - подписи к полям ввода
    param_values - переменные, в которые будут записываться значения
    param_entries - поля ввода параметров
    help_values - temp переменные для числовых значений
    '''
    def _show_entries(self, params, params_frame, frame_text, params_labels, params_values, params_entries, help_values,
                      label):
        """Показать элементы ввода параметров"""
        label = Label(params_frame, text=frame_text)
        label.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E, padx=3, pady=5)

        # Начинаем цикл с 1, т.к. params[0] - это self
        for p in range(1, len(params)):
            param_name = params[p][0]

            # Необходимо установить Label для подписи параметра
            params_labels[param_name] = Label(params_frame, text=param_name)

            # Если параметр принимает только фиксированные значения,
            # то определение значения через OptionMenu
            if len(params[p][3]) > 0:
                # Если параметр принимает числовое значение, то его переменная целого типа
                if str(params[p][1]) == '<class \'int\'>':
                    params_values[param_name] = IntVar()
                # Так же проверим остальные типы
                elif str(params[p][1]) == '<class \'bool\'>':
                    params_values[param_name] = BooleanVar()
                elif str(params[p][1]) == '<class \'float\'>':
                    params_values[param_name] = DoubleVar()
                else:
                    params_values[param_name] = StringVar()

                params_entries[param_name] = OptionMenu(params_frame,
                                                        params_values[param_name], *params[p][3])

                # Если есть дефолтное значение, то его устанавливаем первым
                if str(type(params[p][2])) != '<class \'inspect._empty\'>':
                    if str(params[p][1]) == '<class \'bool\'>':
                        params_values[param_name].set(bool(params[p][2]))
                    elif str(params[p][1]) == '<class \'str\'>':
                        params_values[param_name].set(str(params[p][2]))
                    elif str(params[p][1]) == '<class \'int\'>':
                        params_values[param_name].set(int(params[p][2]))
                    elif str(params[p][1]) == '<class \'float\'>':
                        params_values[param_name].set(float(params[p][2]))
                else:
                    # Иначе устанавливаем первое из списка
                    params_values[param_name].set(params[p][3][0])

            else:
                # Если параметр необходимо ввести, то смотрим тип
                if str(params[p][1]) == '<class \'bool\'>':
                    # В случае логического значения тоже возьмем OptionMenu
                    params_values[param_name] = BooleanVar()
                    params_values[param_name].set(True)

                    # Возьмем вспомогательную строковую переменную для отображения в списке
                    # Иначе будут отображаться числовые значения
                    help_values[param_name] = (StringVar(), bool)

                    params_entries[param_name] = OptionMenu(params_frame,
                                                            help_values[param_name][0],
                                                            *['True', 'False'])

                elif str(params[p][1]) == '<class \'str\'>':
                    params_values[param_name] = StringVar()
                    # Для строки возьмем Entry
                    params_entries[param_name] = Entry(params_frame,
                                                       textvariable=params_values[param_name])

                elif str(params[p][1]) == '<class \'int\'>':
                    # Для int определен отдельный widget на основе Entry
                    params_values[param_name] = IntVar()
                    help_values[param_name] = (StringVar(), int)

                    params_entries[param_name] = inte.Lotfi(master=params_frame,
                                                            restrict_type=int,
                                                            textvar=help_values[param_name][0])

                elif str(params[p][1]) == '<class \'float\'>':
                    # Для float тоже будем использовать тот настроенный widget
                    params_values[param_name] = DoubleVar()
                    help_values[param_name] = (StringVar(), float)

                    params_entries[param_name] = inte.Lotfi(master=params_frame,
                                                            restrict_type=float,
                                                            textvar=help_values[param_name][0])

                # Если есть дефолтное значение, то устанавливаем его
                if str(params[p][2]) != '<class \'inspect._empty\'>':
                    if str(params[p][1]) == '<class \'bool\'>':
                        if params[p][2]:
                            help_values[param_name][0].set('True')
                        else:
                            help_values[param_name][0].set('False')
                    elif str(params[p][1]) == '<class \'str\'>':
                        params_values[param_name].set(str(params[p][2]))
                    elif str(params[p][1]) == '<class \'int\'>':
                        help_values[param_name][0].set(str(params[p][2]))
                    elif str(params[p][1]) == '<class \'float\'>':
                        help_values[param_name][0].set(str(params[p][2]))

            params_labels[param_name].grid(row=p, column=0)
            params_entries[param_name].grid(row=p, column=1)


    """Проверить заполненность всех имеющихся полей ввода"""
    def _check_entries(self):

        filled = True
        for alg_param in list(self._alg_params_values.keys()):
            val = None
            try:
                val = str(self._alg_params_values[alg_param].get())
            except:
                filled = False

            if val is None or val == '':
                filled = False

        if filled:
            for qf_param in list(self._qf_params_values.keys()):
                val = None
                try:
                    val = str(self._qf_params_values[qf_param].get())
                except:
                    filled = False

                if val is None or val == '':
                    filled = False

        if filled:
            try:
                num_features = int(self._num_value.get())
            except:
                filled = False

        return filled

    """Перенести временные данные в окончательные"""
    def _fill_cur_data(self, help_values, real_values):

        for help_name in help_values.keys():
            val = help_values[help_name][0].get()
            typ = help_values[help_name][1]

            if val.strip() != '':
                real_values[help_name].set(typ(val))
            else:
                real_values[help_name].set(None)

    """Запустить алгоритм поиска подгрупп с полученными параметрами алгоритма и функции качества"""
    def _analyse_data(self):
        # Записать все промежуточные значения в итоговые переменные
        self._fill_cur_data(help_values=self._alg_help_values, real_values=self._alg_params_values)
        self._fill_cur_data(help_values=self._qf_help_values, real_values=self._qf_params_values)

        if not self._check_entries():
            msgb.showerror(title='Заполнены не все поля',
                           message='Нельзя выполнить анализ, пока не заполнены все поля параметров алгоритма и функции качества')
        else:
            num_features = int(self._num_value.get())

            if num_features <= 0:
                msgb.showerror(title='Некорректное количество признаков',
                               message='Количество признаков в итоговых правилах не может быть отрицательным или равным нулю')
            else:
                alg_params = self._params_to_dict(self._alg_params_values)

                alg = self._alg_dict[self._alg_var.get()][0](**alg_params)

                qf_params = self._params_to_dict(self._qf_params_values)

                qf = self._func_dict[self._func_var.get()][0](**qf_params)

                analysis = analyser.Analyser(source_s=self._file[0],
                                             file_sep_s=self._sep,
                                             features_lst=self._features,
                                             algorythm=alg,
                                             qual_func=qf,
                                             feature_number_i=num_features)

                self._progress = tk.Toplevel(self._master)
                func = analyser.Analyser.get_analysis_results
                self._app = progress.ProgressWindow(self._progress, analysis, func)
                self._master.withdraw()
                self._master.wait_window(self._progress)
                result = self._app.result

                self._master.deiconify()

                if result is None or result.shape[0] == 0 or result.shape[0] == 1 and result['quality'][0] == 0:
                    msgb.showinfo(title='Группы не найдены',
                                  message='Не удалось обнаружить подгруппы с помощью заданного алгоритма и функции качества. '
                                          'Попробуйте изменить параметры или использовать другой алгоритм или функцию качества')
                else:
                    self._analysis_result = tk.Toplevel(self._master)
                    self.app = result_observer.ResultObserver(self._analysis_result, result, self._file, self._sep)
                    self._master.withdraw()
                    self._master.wait_window(self._analysis_result)
                    self._master.deiconify()

    """
    Формирование единого списка параметров для передачи в алгоритм анализа и функцию качества
    """
    def _params_to_dict(self, var_dict):
        params = dict()
        for param in list(var_dict.keys()):
            val = var_dict[param].get()
            params[param] = val

        return params
