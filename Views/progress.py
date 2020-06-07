import tkinter as tk
from tkinter import *

class ProgressWindow(tk.Frame):
    def __init__(self, master, analysis, action):
        self._analyser = analysis
        self._act = action
        self._master = master
        self._master.title('Выполняется поиск подгрупп')
        self._frame = tk.Frame(self._master)

        self._status_var = StringVar()
        self._status_var.set('Ожидание подтверждения')
        self._label = Label(self._frame, text='Поиск подгрупп может занять некоторое время')
        self._status_l = Label(self._frame, text='Текущий статус анализа:')
        self._status = Label(self._frame, textvariable=self._status_var, width=40, anchor='w', justify='left')
        self._do_btn = Button(self._frame, text='Запустить', command=self._start)

        self._label.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
        self._status_l.grid(row=1, column=0, sticky=E, padx=5, pady=3)
        self._status.grid(row=1, column=1, sticky=W, padx=5, pady=3)
        self._do_btn.grid(row=2, column=0, columnspan=2)
        self._frame.pack()

        self.result = None

    """Изменение значения статуса (будет передаваться как callback)"""
    def change_status(self, status):
        self._status_var.set(status)
        self._status.update()

    """Запуск анализа"""
    def _start(self):
        result = self._act(analyser=self._analyser, callback_fn=self.change_status)
        self._master.destroy()
        self.result = result


