import inspect
import pkgutil
from SubgroupDiscovery.Algorythms import alg_interface as ialg
from SubgroupDiscovery.QualityFunctions import qual_interface as iqual


class Observer:
    """
    Просмотр исходного кода для поиска реализация алгоритмов поиска подгрупп и функций качества
    """

    """
    Определение имеющихся алгоритмов для поиска подгрупп
    """
    @staticmethod
    def get_algs_list():


        lst = dict()
        for module_finder, name, ispkg in pkgutil.iter_modules(path=['SubgroupDiscovery/Algorythms']):
            if ispkg or name == __name__:
                continue  # пропускаем пакеты
            mod = module_finder.find_module(name).load_module(name)

            # Анализируем все классы в модуле
            for class_name, cls in inspect.getmembers(mod, inspect.isclass):
                # Если класс реализует интерфейс алгоритма SD
                if ialg.IAlgorithm.implementedBy(cls):
                    # то сохраняем сигнатуру вызова класса
                    par = inspect.signature(cls.__init__).parameters

                    # Параметры для вызова алгоритма
                    params = []

                    for param in inspect.signature(cls.__init__).parameters:
                        # сохраняем список возможных значений параметра (если есть ограничения)
                        possible_values = cls.values_restrict.get(par[param].name, [])
                        params.append((par[param].name, par[param].annotation, par[param].default, possible_values))

                    lst[cls.alg_name] = cls, params

        return lst

    """Определение имеющихся функций качества для поиска подгрупп"""
    @staticmethod
    def get_qf_list():
        lst = dict()
        for module_finder, name, ispkg in pkgutil.iter_modules(path=['SubgroupDiscovery/QualityFunctions']):
            if ispkg or name == __name__:
                continue  # пропускаем пакеты
            mod = module_finder.find_module(name).load_module(name)

            # Анализируем все классы в модуле
            for class_name, cls in inspect.getmembers(mod, inspect.isclass):
                # Если класс реализует интерфейс функции качества SD
                if iqual.IQuality.implementedBy(cls):
                    # то сохраняем сигнатуру вызова класса
                    par = inspect.signature(cls.__init__).parameters

                    # Параметры, необходимые для вызова функции
                    params = []

                    for param in inspect.signature(cls.__init__).parameters:
                        # сохраняем список возможных значений параметра (если есть ограничения)
                        possible_values = cls.values_restrict.get(par[param].name, [])
                        params.append((par[param].name, par[param].annotation, par[param].default, possible_values))

                    lst[cls.qual_name] = cls, params

        return lst
