import unittest
from Core.analyser import Analyser
import pandas as pd


class TestAnalyser(unittest.TestCase):
    def setUp(self):
        self.analyser = Analyser(source_s='', file_sep_s='', features_lst=list(),
                                 algorythm=None, qual_func=None, feature_number_i=0)

    '''Тестируем, чтобы все интервалы отображались красиво. Целые числа в интервале'''
    def test_parse_rule_int(self):
        rule = 'Feature1: [10:56[ AND Feature2.isnull()'
        expected_result = 'Feature1 in [10; 56] and Feature2.isnull()'
        result = Analyser.parse_rule(rule)

        self.assertEqual(result, expected_result)

    '''Тестируем, чтобы все интервалы отображались красиво. Дробные числа в интервале'''
    def test_parse_rule_float(self):
        rule = 'Feature1: [78.68:11.32[ AND Feature2>=4'
        expected_result = 'Feature1 in [78.68; 11.32] and Feature2>=4'
        result = Analyser.parse_rule(rule)

        self.assertEqual(result, expected_result)

    '''Тестирование преобразования интервала в запросе'''
    def test_get_query(self):
        # Проверим преобразование and в & и обработку интервалов
        rule = 'Feature in [10; 56.56] and Feature2.isnull()'
        expected_result = 'Feature>=10 & Feature<=56.56 & Feature2.isnull()'
        result = Analyser.get_query(rule)

        self.assertEqual(result, expected_result)

    '''Тестирование отображения статистики по подгруппам'''
    def test_get_stats(self):
        data_dict = {'feat1': [0, 1, 2, 3, 4, 5, 6, 7],
                     'feat2': ['1', '0', '3', '1', None, '0', '1', '3'],
                     'Target': [0, 1, 1, 0, 1, 0, 1, 0]}

        data_df = pd.DataFrame(data_dict)

        result = self.analyser._get_stats('', data_df)

        self.assertEqual(result[0], 4)
        self.assertEqual(result[1], 2)
        self.assertEqual(result[2], 0.5)


if __name__ == "__main__":
  unittest.main()
