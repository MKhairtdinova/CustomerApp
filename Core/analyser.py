from SubgroupDiscovery import subgroup as subg
from SubgroupDiscovery import subgroup_task as sgt
import pandas as pd
import time
import random
import re

'''
Модуль проведения анализа данных
'''


class Analyser:
    """
    Класс проведения анализа
    file_path - директория источника данных
    file_sep
    """

    def __init__(self, source_s: str, file_sep_s: str, features_lst: list, algorythm, qual_func, feature_number_i: int):
        self._source_s = source_s
        self._features_lst = features_lst
        self._algorythm = algorythm
        self._qf = qual_func
        self._sep_s = file_sep_s
        self._feat_num_i = feature_number_i

    '''
    Получение подгрупп: выполнение анализа, сбор статистики по подгруппам и возврат для UI
    analyser - экземпляр класса IAlgorithm, который будет выполнять анализ
    callback_fn - функция для обновления статуса анализа (запишет в окно ProcessWindow)
    '''

    @staticmethod
    def get_analysis_results(analyser, callback_fn):

        result_df, data_df = analyser._execute_analysis(callback_fn)

        # если нашлись подгруппы, то обработаем полученные правила
        if not (result_df.shape[0] == 0 or result_df.shape[0] == 1 and result_df['quality'][0] == 0):
            callback_fn('Обработка полученных правил')
            # Оформление данных
            result_df['description'] = list(map(lambda x: Analyser.parse_rule(x), result_df['description'].tolist()))

            callback_fn('Подготовка статистики по группам')
            stats_lst = list(map(lambda rule: analyser._get_stats(rule, data_df), result_df['description'].tolist()))

            result_df['count'] = list(map(lambda x: x[0], stats_lst))
            result_df['original'] = list(map(lambda x: x[1], stats_lst))
            result_df['percentage'] = list(map(lambda x: x[2], stats_lst))

        return result_df

    '''
    Выполнение самого анализа
    callback_fn - функция для обновления статуса анализа (запишет в окно ProcessWindow)
    '''

    def _execute_analysis(self, callback_fn):
        target = subg.BinaryTarget('Target', True)
        data_df = self._get_data(callback_fn)

        callback_fn('Компоновка параметров анализа')
        search_space = subg.create_selectors(data_df, ignore=['Target'])

        task = sgt.SubgroupDiscoveryTask(data=data_df,
                                         target=target,
                                         search_space=search_space,
                                         qf=self._qf,
                                         depth=self._feat_num_i)

        callback_fn('Выполнение анализа')
        result_df = self._algorythm.execute(task).to_dataframe()

        return result_df, data_df

    '''
    Получение датасета исходных данных
    '''

    def _get_data(self, callback_fn):
        callback_fn('Извлечение данных')
        data_df = pd.read_csv(self._source_s, sep=self._sep_s)

        analysed_data_df = data_df[self._features_lst].copy()

        del data_df

        callback_fn('Генерация искусственных данных')
        processed_data_df = self._generate_data(analysed_data_df)

        return processed_data_df

    '''
    Генерация класса синтетических данных
    '''

    def _generate_data(self, data_df):
        generated_set_df = data_df.copy()

        data_df['Target'] = [1] * data_df.shape[0]

        for col_name in list(generated_set_df):
            generated_set_df[col_name] = sorted(generated_set_df[col_name], key=lambda *args: random.random())

        generated_set_df['Target'] = [0] * generated_set_df.shape[0]

        data_df = data_df.append(generated_set_df, ignore_index=True)

        return data_df

    '''
    Получение статистики по найденной подгруппе
    rule_s - описание подгруппы
    data_df - файл исходных данных
    '''
    def _get_stats(self, rule_s: str, data_df: pd.DataFrame):
        query_s = Analyser.get_query(rule_s)

        group_df = data_df.query(query_s)

        cnt_i = group_df.shape[0]  # общее количество элементов
        orig_i = group_df[group_df['Target'] == 1].shape[0]  # количество оригинальных элементов
        perc_i = round(orig_i / (data_df.shape[0] / 2),
                       2)  # доля оригинальных данных в группе от общего количества оригинальных данных

        return (cnt_i, orig_i, perc_i)

    ''' 
    Форматирование правила, полученного алгоритмом в более красивое
    Все интервалы должны отображаться красиво
    '''
    def parse_rule(rule_s: str):
        parts_lst = str(rule_s).replace(' AND ', ';').split(';')

        for indx in range(len(parts_lst)):
            if parts_lst[indx].find(':') != -1:
                pattern_s = r'([a-zA-Zа-яА-Я0-9_]+)\: \[([\d\.]+)\:([\d\.]+)\['

                conj_parts_lst = re.split(pattern_s, parts_lst[indx])

                new_rule_s = conj_parts_lst[1] + ' in [' + conj_parts_lst[2] + '; ' + conj_parts_lst[3] + ']'

                parts_lst[indx] = new_rule_s

        return str.join(' and ', parts_lst)

    '''
    Получение запроса на выборку из датафрейма на основе правила
    rule_s - описание подгруппы
    '''

    @staticmethod
    def get_query(rule_s: str):
        # разделим на составляющие части конъюнкции
        parts_lst = rule_s.replace(' and ', ',').split(',')

        # проверим каждую часть на соответствие
        for indx in range(len(parts_lst)):
            conj_part_s = parts_lst[indx]

            # все интервальные правила должны быть заменены по принципу * <= * and * >= *
            if conj_part_s.find(' in [') != -1:
                pattern_s = r'(^[a-zA-Z0-9_]+) in \[([\d+\.]+)\; ([\d+\.]+)\]$'

                part_lst = re.split(pattern_s, conj_part_s)

                query_s = part_lst[1] + '>=' + part_lst[2] + ' & ' + part_lst[1] + '<=' + part_lst[3]

                parts_lst[indx] = query_s

        # слагаемые конъюнкции должны быть соедиены через &, а не and
        return str.join(' & ', parts_lst)
