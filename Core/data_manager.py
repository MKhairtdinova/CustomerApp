from Core.analyser import Analyser
import pandas as pd

'''
Модуль работы с данными в формате csv
'''


class DataManager:
    '''
       Класс работы с данными в директориях: сохранение и удаление подгрупп из файла csv с сохранением в отдельный файл
    '''

    '''
    Сохранение данных подгруппы 
    source_s - директория файла-источника данных о подгруппе в формате CSV
    sep_s - разделитель в csv-файле
    dir_s - директория, куда сохранить данные о подгруппе
    rule_s - описание подгруппы, по которому будут извлечены данные из источника
    '''
    @staticmethod
    def save_group(source_s: str, sep_s: str, dir_s: str, rule_s: str):
        query = Analyser.get_query(rule_s)

        data = pd.read_csv(source_s, sep=sep_s)

        group = data.query(query)

        group.to_csv(dir_s, sep=sep_s, index=False)

    '''
    Удаление данных подгруппы. После удаления создается отдельный файл без этой группы
    source_s - директория файла-источника данных о подгруппе в формате CSV
    sep_s - разделитель в csv-файле
    dir_s - директория, куда сохранить данные о остальных элементах
    rule_s - описание подгруппы, по которому будут извлечены данные из источника
    '''
    @staticmethod
    def delete_group(source_s: str, sep_s: str, dir_s: str, rule_s: str):
        query_s = Analyser.get_query(rule_s)

        non_query_s = 'not (' + query_s + ')'

        data_df = pd.read_csv(source_s, sep=sep_s)

        non_group = data_df.query(non_query_s)

        non_group.to_csv(dir_s, sep=sep_s, index=False)

