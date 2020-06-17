'''
Created on 29.04.2016
@author: lemmerfn
'''
import copy
from SubgroupDiscovery import utils as u
from SubgroupDiscovery import subgroup_task as st
import zope.interface
from SubgroupDiscovery.Algorythms import alg_interface as ialg
from SubgroupDiscovery import boolean_expressions as bexp
from SubgroupDiscovery.QualityFunctions import base_qual as bq

@zope.interface.implementer(ialg.IAlgorithm)
class SimpleDFS:
    alg_name = 'SimpleDFS'
    values_restrict = dict()

    def execute(self, task, use_optimistic_estimates=True):
        task.qf.calculate_constant_statistics(task)
        result = self.search_internal(task, [], task.search_space, [], use_optimistic_estimates)
        result.sort(key=lambda x: x[0], reverse=True)
        return st.SubgroupDiscoveryResult(result, task)

    def search_internal(self, task, prefix, modification_set, result, use_optimistic_estimates):
        sg = bexp.Conjunction(copy.copy(prefix))

        statistics = task.qf.calculate_statistics(sg, task.data)
        if use_optimistic_estimates and len(prefix) < task.depth and isinstance(task.qf,
                                                                                bq.BoundedInterestingnessMeasure):
            optimistic_estimate = task.qf.optimistic_estimate(sg, statistics)
            if not (optimistic_estimate > u.minimum_required_quality(result, task)):
                return result
        quality = task.qf.evaluate(sg, statistics)
        u.add_if_required(result, sg, quality, task)

        if len(prefix) < task.depth:
            new_modification_set = copy.copy(modification_set)
            for sel in modification_set:
                prefix.append(sel)
                new_modification_set.pop(0)
                self.search_internal(task, prefix, new_modification_set, result, use_optimistic_estimates)
                # remove the sel again
                prefix.pop(-1)
        return result

    def __init__(self):
        pass
