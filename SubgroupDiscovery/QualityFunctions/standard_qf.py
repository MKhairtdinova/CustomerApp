from SubgroupDiscovery.QualityFunctions import base_qual as bq
import scipy.stats
from SubgroupDiscovery import utils as u
from SubgroupDiscovery.QualityFunctions import qual_interface as iqual
import zope.interface

'''
Created on 28.04.2016
@author: lemmerfn
'''
from abc import ABC, abstractmethod
from collections import namedtuple
from itertools import combinations
import numpy as np


@zope.interface.implementer(iqual.IQuality)
class StandardQF(bq.SimplePositivesQF, bq.BoundedInterestingnessMeasure):
    """
    StandardQF which weights the relative size against the difference in averages
    The StandardQF is a general form of quality function which for different values of a is order equivalen to
    many popular quality measures.
    Attributes
    ----------
    a : float
        used as an exponent to scale the relative size to the difference in averages
    """

    qual_name = 'Стандарт'
    values_restrict = dict()

    @staticmethod
    def standard_qf(a, instances_dataset, positives_dataset, instances_subgroup, positives_subgroup):
        if not hasattr(instances_subgroup, '__array_interface__') and (instances_subgroup == 0):
            return np.nan
        p_subgroup = np.divide(positives_subgroup, instances_subgroup)
        # if instances_subgroup == 0:
        #    return 0
        # p_subgroup = positives_subgroup / instances_subgroup
        p_dataset = positives_dataset / instances_dataset
        return (instances_subgroup / instances_dataset) ** a * (p_subgroup - p_dataset)

    def __init__(self, a: float):
        """
        Parameters
        ----------
        a : float
            exponent to scale the relative size to the difference in means
        """

        self.a = a
        super().__init__()

    def evaluate(self, subgroup, statistics=None):
        statistics = self.ensure_statistics(subgroup, statistics)
        datatset = self.datatset_statistics
        return StandardQF.standard_qf(self.a, datatset.size, datatset.positives_count, statistics.size,
                                      statistics.positives_count)

    def optimistic_estimate(self, subgroup, statistics=None):
        statistics = self.ensure_statistics(subgroup, statistics)
        datatset = self.datatset_statistics
        return StandardQF.standard_qf(self.a, datatset.size, datatset.positives_count, statistics.positives_count,
                                      statistics.positives_count)

    def optimistic_generalisation(self, subgroup, statistics=None):
        statistics = self.ensure_statistics(subgroup, statistics)
        datatset = self.datatset_statistics
        pos_remaining = datatset.positives_count - statistics.positives_count
        return StandardQF.standard_qf(self.a, datatset.size, datatset.positives_count, statistics.size + pos_remaining,
                                      datatset.positives_count)

    def supports_weights(self):
        return True
