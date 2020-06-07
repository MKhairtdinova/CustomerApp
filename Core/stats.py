import pandas as pd

'''
Извлечение статистики из данных
'''


class Statistics:
    @staticmethod
    def get_df_statistics(file_path, sep):
        data = pd.read_csv(file_path, sep=sep)

        stats_info = dict()

        for header in list(data):
            s = data[header]

            try:
                vals = list(map(float, s.tolist()))

                max = s.max()
                min = s.min()
                avg = s.mean().round(2)
                med = s.median()
                cnt = s.shape[0]
                nul = cnt - s.count()

                stats_info[header] = (('Всего', cnt), ('Max', max), ('Min', min),
                                      ('Ср. арифм.', avg), ('Медиана', med), ('Пустых', nul),
                                      ('plt', s))

            except:
                cnt = s.shape[0]
                nul = cnt - s.count()

                stats_info[header] = (('Всего', cnt), ('Пустых', nul))
            # finally:
            #   print(header, stats_info[header])

        return stats_info
