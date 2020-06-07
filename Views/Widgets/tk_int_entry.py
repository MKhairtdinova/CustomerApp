import tkinter as tk

"""Строка ввода с ограничением по типу вводимого значения"""
class Lotfi(tk.Entry):
    def __init__(self, textvar, restrict_type, master=None, **kwargs):
        self.var = textvar
        self.restrict = restrict_type
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set
        self.config(width=20)

    """Проверка введенного значения на допустимость"""
    def check(self, *args):
        try:
            val = self.var.get().strip()
            if val.strip() != '':
                self.restrict(val)

            self.old_value = val
        except:
            self.var.set(self.old_value)
            i = self.var.get()
