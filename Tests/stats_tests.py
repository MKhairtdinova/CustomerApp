import unittest
from Core.stats import Statistics
import pandas as pd

class TestStatistics(unittest.TestCase):
    # протестируем обработку числовых данных и строковых
    def setUp(self):
        file = 'test_stats.csv'

        '''
        data_dict = {'feat1': [1, 2, None, 6, 7, None, 8, 11.5, None],
                     111}

        data_df = pd.DataFrame(data_dict)

        data_df.to_csv(file, sep=',')
        '''

        self.file = file
        self.sep=','

    def test_get_df_statistics(self):
        result = Statistics.get_df_statistics(self.file, self.sep)
        cnt = 9

        self.assertEqual(result['feat1'][0][1], cnt)
        self.assertEqual(result['feat1'][1][1], 11.5)
        self.assertEqual(result['feat1'][2][1], 1.0)
        self.assertEqual(result['feat1'][3][1], 5.92)
        self.assertEqual(result['feat1'][4][1], 6.5)
        self.assertEqual(result['feat1'][5][1], 3)
        self.assertIsInstance(result['feat1'][6][1], pd.Series)

        self.assertEqual(result['feat2'][0][1], cnt)
        self.assertEqual(result['feat2'][1][1], 2)


if __name__ == "__main__":
  unittest.main()
