import zope.interface

def restrict_invariant(ob):
    if not isinstance(ob.values_restrict, dict):
        raise TypeError("Значение ограничений values_restrict должно представляться типом dict")


def alg_name_invariant(ob):
    if not isinstance(ob.qual_name, str) or ob.qual_name.strip() == '':
        raise TypeError("Имя алгоритма должно быть строковым и не пустым")

class IAlgorithm(zope.interface.Interface):
    """Интерфейс для определения алгоритма поиска подгрупп"""
    alg_name = zope.interface.Attribute("""Название алгоритма для отображения в UI""")

    def __init__(self, **kwargs):
        """Определение параметров алгоритма"""

    def execute(self, task):
        """Основной метод для вызова выполнения алгоритма извне"""

    values_restrict = zope.interface.Attribute(
        """Ограничение значений параметров для вызова функции (если имеются, иначе - {})""")

    zope.interface.invariant(restrict_invariant)
    zope.interface.invariant(alg_name_invariant)


