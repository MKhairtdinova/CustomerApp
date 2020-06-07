from tkinter import *
from Core.data_manager import DataManager
from tkinter import filedialog as fd

class GroupManagerWindow(Frame):
    del_group = 'DELETE'
    save_group = 'SAVE'

    def __init__(self, master, groups: list, action: str, source: str, sep: str):
        self._source = source[0]
        self._sep = sep

        self._master = master

        self._frame = Frame(self._master)

        self._group_val = StringVar()
        self._group_val.set(groups[0])

        self._lbl = Label(self._frame, text='Выберите группу для ' + ('сохранения' if action == GroupManagerWindow.save_group else 'удаления'))

        self._groups_lst = OptionMenu(self._frame, self._group_val, *groups)
        self._groups_lst.config(width=70)

        self._action_btn = Button(self._frame)

        if action == GroupManagerWindow.save_group:
            self._master.title('Сохранение подгруппы')
            self._action_btn['text'] = 'Сохранить'
            self._action_btn.config(command=self._save_group)
        elif action == GroupManagerWindow.del_group:
            self._master.title('Удаление подгруппы')
            self._action_btn['text'] = 'Удалить'
            self._action_btn.config(command=self._delete_group)


        self._lbl.pack(pady=2, padx=3)
        self._groups_lst.pack(padx=3, pady=2)
        self._action_btn.pack(padx=3, pady=2)
        self._frame.pack()

    """Сохранение подгруппы по выбранному описанию"""
    def _save_group(self):
        rule = self._group_val.get()

        directory = fd.asksaveasfilename(defaultextension='.csv')

        if directory:
            DataManager.save_group(source_s=self._source, sep_s=self._sep, dir_s=directory, rule_s=rule)

            self._master.destroy()

    """Удаление подгруппы по выбранному описанию"""
    def _delete_group(self):
        rule = self._group_val.get()

        directory = fd.asksaveasfilename(defaultextension='.csv')

        if directory:
            DataManager.delete_group(source_s=self._source, sep_s=self._sep, dir_s=directory, rule_s=rule)

            self._master.destroy()




