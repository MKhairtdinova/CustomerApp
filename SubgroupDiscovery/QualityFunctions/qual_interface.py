import zope.interface


def restrict_invariant(ob):
    if not isinstance(ob.values_restrict, dict):
        raise TypeError("Значение ограничений values_restrict должно представляться типом dict")


def qual_name_invariant(ob):
    if not isinstance(ob.qual_name, str) or ob.qual_name.strip() == '':
        raise TypeError("Имя функции должно быть строковым и не пустым")


class IQuality(zope.interface.Interface):
    """Интерфейс для определения функции качества поиска подгрупп"""
    qual_name = zope.interface.Attribute("""Название функции качества для отображения в UI""")
    values_restrict = zope.interface.Attribute(
        """Ограничение значений параметров для вызова функции (если имеются, иначе - {})""")

    zope.interface.invariant(restrict_invariant)
    zope.interface.invariant(qual_name_invariant)

    def __init__(self, **kwargs):
        """Определение параметров функции"""

    def evaluate(self, subgroup, statistics):
        """Основной метод для вызова извне"""
