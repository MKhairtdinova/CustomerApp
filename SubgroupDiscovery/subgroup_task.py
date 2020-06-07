'''
Created on 02.05.2016
@author: lemmerfn
'''
import itertools
from functools import partial
from heapq import heappush, heappop
from collections.abc import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import SubgroupDiscovery.utils as u
from functools import total_ordering


class SubgroupDiscoveryTask:
    '''
    Capsulates all parameters required to perform standard subgroup discovery
    '''

    def __init__(self, data, target, search_space, qf, result_set_size=10, depth=3, min_quality=0,
                 weighting_attribute=None):
        self.data = data
        self.target = target
        self.search_space = search_space
        self.qf = qf
        self.result_set_size = result_set_size
        self.depth = depth
        self.min_quality = min_quality
        self.weighting_attribute = weighting_attribute


class SubgroupDiscoveryResult:
    def __init__(self, results, task):
        self.task = task
        self.results = results
        assert (isinstance(results, Iterable))

    def to_descriptions(self):
        return self.results

    def to_subgroups(self):
        return [(quality, Subgroup(self.task.target, description)) for quality, description in self.results]

    def to_dataframe(self, include_info=False):
        qualities = [quality for quality, description in self.results]
        descriptions = [description for quality, description in self.results]
        df = pd.DataFrame.from_dict({'quality': qualities, 'description': descriptions})
        if include_info:
            calc_stats = self.task.target.calculate_statistics
            data = self.task.data
            records = [calc_stats(description, data) for quality, description in self.results]
            df_stats = pd.DataFrame.from_records(records)
            df = pd.concat([df, df_stats], axis=1)
        return df

    def supportSetVisualization(self, in_order=True, drop_empty=True):
        df = self.task.data
        n_items = len(self.task.data)
        n_SGDs = len(self.results)
        covs = np.zeros((n_items, n_SGDs), dtype=bool)
        for i, (_, r) in enumerate(self.results):
            covs[:, i] = r.covers(df)

        img_arr = covs.copy()

        sort_inds_x = np.argsort(np.sum(covs, axis=1))[::-1]
        img_arr = img_arr[sort_inds_x, :]
        if not in_order:
            sort_inds_y = np.argsort(np.sum(covs, axis=0))
            img_arr = img_arr[:, sort_inds_y]
        if drop_empty:
            keep_entities = np.sum(img_arr, axis=1) > 0
            print("Discarding {} entities that are not covered".format(n_items - np.count_nonzero(keep_entities)))
            img_arr = img_arr[keep_entities, :]
        return img_arr.T

@total_ordering
class Subgroup():
    def __init__(self, target, subgroup_description):
        # If its already a BinaryTarget object, we are fine, otherwise we create a new one
        # if (isinstance(target, BinaryTarget) or isinstance(target, NumericTarget)):
        #    self.target = target
        # else:
        #    self.target = BinaryTarget(target)

        # If its already a SubgroupDescription object, we are fine, otherwise we create a new one
        self.target = target
        self.subgroup_description = subgroup_description

        # initialize empty cache for statistics
        self.statistics = {}

    def __repr__(self):
        return "<<" + repr(self.target) + "; D: " + repr(self.subgroup_description) + ">>"

    def covers(self, instance):
        if hasattr(self.subgroup_description, "representation"):
            return self.subgroup_description
        else:
            return self.subgroup_description.covers(instance)

    def __getattr__(self, name):
        return getattr(self.subgroup_description, name)

    def __eq__(self, other):
        if other is None:
            return False
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return repr(self) < repr(other)

    def get_base_statistics(self, data, weighting_attribute=None):
        return self.target.get_base_statistics(data, self, weighting_attribute)

    def calculate_statistics(self, data, weighting_attribute=None):
        self.target.calculate_statistics(self, data, weighting_attribute)
