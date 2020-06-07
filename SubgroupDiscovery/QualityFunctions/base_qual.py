from abc import ABC, abstractmethod
from itertools import combinations
from SubgroupDiscovery import subgroup as sg
from collections import namedtuple
from functools import total_ordering
import numpy as np
import scipy.stats


class AbstractInterestingnessMeasure(ABC):
    @abstractmethod
    def supports_weights(self):
        pass

    @abstractmethod
    def is_applicable(self, subgroup):
        pass

    def ensure_statistics(self, subgroup, statistics_or_data):
        if not self.has_constant_statistics:
            self.calculate_constant_statistics(subgroup.data)
        if any(not hasattr(statistics_or_data, attr) for attr in self.required_stat_attrs):
            if getattr(subgroup, 'statistics', False):
                return subgroup.statistics
            else:
                return self.calculate_statistics(subgroup, statistics_or_data)
        return statistics_or_data


class SimplePositivesQF(AbstractInterestingnessMeasure, ABC):  # pylint: disable=abstract-method
    tpl = namedtuple('PositivesQF_parameters', ('size', 'positives_count'))

    def __init__(self):
        self.datatset_statistics = None
        self.positives = None
        self.has_constant_statistics = False
        self.required_stat_attrs = ('size', 'positives_count')

    def calculate_constant_statistics(self, task):
        assert isinstance(task.target, sg.BinaryTarget)
        data = task.data
        self.positives = task.target.covers(data)
        self.datatset_statistics = SimplePositivesQF.tpl(len(data), np.sum(self.positives))
        self.has_constant_statistics = True

    def calculate_statistics(self, subgroup, data=None):
        if hasattr(subgroup, "representation"):
            cover_arr = subgroup
            size = subgroup.size
        elif isinstance(subgroup, slice):
            cover_arr = subgroup
            # https://stackoverflow.com/questions/36188429/retrieve-length-of-slice-from-slice-object-in-python
            size = len(range(*subgroup.indices(len(self.positives))))
        else:
            cover_arr = subgroup.covers(data)
            size = np.count_nonzero(cover_arr)
        return SimplePositivesQF.tpl(size, np.count_nonzero(self.positives[cover_arr]))

    def is_applicable(self, subgroup):
        return isinstance(subgroup.target, sg.BinaryTarget)


class BoundedInterestingnessMeasure(AbstractInterestingnessMeasure, ABC):
    pass
