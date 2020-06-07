from tkinter import *
from tkscrolledframe import ScrolledFrame
from tkmagicgrid import *
import pandas as pd
from tkinter import filedialog as fd
from Views.manage_group import GroupManagerWindow


class ResultObserver(Frame):
    def __init__(self, master, results: pd.DataFrame, source, sep):
        self._source= source
        self._results = results
        self._sep = sep
        self._master = master

        self._master.title('Результаты анализа')
        self._frame = Frame(self._master)

        self._label = Label(self._frame, text='Обнаружены схожие элементы, описываемые правилами:')

        self._preview = ScrolledFrame(self._frame, width=700, height=270, bg='gray', bd=5)
        self._preview.bind_arrow_keys(self._frame)
        self._preview.bind_scroll_wheel(self._frame)
        self._inner_frame = self._preview.display_widget(Frame)
        self._grid = MagicGrid(self._inner_frame)

        headers = self._grid.add_header(*['№', 'Полученное правило', 'Кол-во эл-в',
                                          'Кол-во оригинальных', 'Доля от всех оригинальных',
                                          'Результат функции качества'])

        ind = 1
        for index, row in results.iterrows():
            self._grid.add_row(*[ind, row['description'], row['count'], row['original'], row['percentage'], row['quality']])
            print(row['description'])
            ind += 1

        # общее форматирование
        for col in [0, 2, 3, 4, 5]:
            self._grid.configure_column(col, anchor="center", justify="center")

        # отдельно заголовок описания, т.к ранее его проигнорировали
        headers[1].configure(anchor="center", justify="center")

        # отдельно столбцец номера, чтобы выглядел лучше
        self._grid.configure_column(0, width=5)

        self._buttons_frame = Frame(self._frame)
        self._save_btn = Button(self._buttons_frame, text='Сохранить группу', command= self._save_data)
        self._del_btn = Button(self._buttons_frame, text='Удалить группу', command=self._delete_data)

        self._frame.pack()
        self._label.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)
        self._preview.pack(padx=5, pady=5)
        self._grid.pack(side=TOP, fill=BOTH, expand=1)
        self._save_btn.grid(row=0, column=0, sticky=E, padx=3, pady=5)
        self._del_btn.grid(row=0, column=1, sticky=W, padx=3, pady=5)
        self._buttons_frame.pack()

    """Открытие окна сохранения данных по группе"""
    def _save_data(self):
        self._manage = Toplevel(self._master)
        rules = self._results['description'].tolist()
        self._app = GroupManagerWindow(self._manage, rules, GroupManagerWindow.save_group, source=self._source, sep=self._sep)
        self._master.withdraw()
        self._master.wait_window(self._manage)
        self._master.deiconify()

    """Открытие окна удаления данных о подгруппе"""
    def _delete_data(self):
        self._manage = Toplevel(self._master)
        rules = self._results['description'].tolist()
        self._app = GroupManagerWindow(self._manage, rules, GroupManagerWindow.del_group, source=self._source, sep=self._sep)
        self._master.withdraw()
        self._master.wait_window(self._manage)
        self._master.deiconify()

