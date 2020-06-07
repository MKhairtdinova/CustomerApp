from Core.data_manager import DataManager
import unittest
import os
import pandas as pd

class TestDataManager(unittest.TestCase):
    def setUp(self):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_save.csv')

        try:
            os.remove(path)
        except:
            pass

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_del.csv')

        try:
            os.remove(path)
        except:
            pass

    def test_save(self):
        '''
        data_dict = {'feat1': [0, 1, 2, 3, 4, 5, 6, 7],
                     'feat2': ['A1', '0', '3', '1', 'None', '0', '1', '3'],
                     'Target': [0, 1, 1, 0, 1, 0, 1, 0]}
        '''

        source = 'test_manager.csv'
        sep=','
        dir = 'test_save.csv'

        DataManager.save_group(source_s=source, sep_s=sep, dir_s=dir, rule_s='feat1 in [2; 5] and Target==1')

        data = None

        try:
            data = pd.read_csv(dir, sep=sep)
        except:
            # при любом исключении должна отображаться ошибка
            self.assertFalse(True, 'Ошибка чтения файла после сохранения')

        feat1_vals = data['feat1'].tolist()
        feat2_vals = data['feat2'].tolist()
        target_vals = data['Target'].tolist()

        expected_feat1 = [2, 4]
        expected_feat2 = ['3', '\'None\'']
        expected_target = [1, 1]


        self.assertListEqual(feat1_vals, expected_feat1)
        self.assertListEqual(feat2_vals, expected_feat2)
        self.assertListEqual(target_vals, expected_target)

    def test_delete(self):
        '''
        data_dict = {'feat1': [0, 1, 2, 3, 4, 5, 6, 7],
                     'feat2': ['A1', '0', '3', '1', None, '0', '1', '3'],
                     'Target': [0, 1, 1, 0, 1, 0, 1, 0]}
        '''

        source = 'test_manager.csv'
        sep=','
        dir = 'test_del.csv'

        DataManager.delete_group(source_s=source, sep_s=sep, dir_s=dir, rule_s='feat1 >=5 and Target==0')

        data = None

        try:
            data = pd.read_csv(dir, sep=sep)
        except:
            # при любом исключении должна отображаться ошибка
            self.assertFalse(True, 'Ошибка чтения файла после сохранения')

        feat1_vals = data['feat1'].tolist()
        feat2_vals = data['feat2'].tolist()
        target_vals = data['Target'].tolist()

        expected_feat1 = [0, 1, 2, 3, 4, 6]
        expected_feat2 = ['A1', '0', '3', '1', '\'None\'', '1']
        expected_target = [0, 1, 1, 0, 1, 1]

        self.assertListEqual(feat1_vals, expected_feat1)
        self.assertListEqual(feat2_vals, expected_feat2)
        self.assertListEqual(target_vals, expected_target)

if __name__ == "__main__":
  unittest.main()







