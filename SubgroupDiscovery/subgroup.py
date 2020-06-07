from abc import ABC, abstractmethod
import weakref
from functools import total_ordering
import numpy as np
import pandas as pd
from SubgroupDiscovery import utils as u


@total_ordering
class SelectorBase(ABC):
    __refs__ = weakref.WeakSet()
    def __new__(cls, *args, **kwargs):

        tmp = super().__new__(cls)

        tmp.set_descriptions(*args, **kwargs)
        if tmp in SelectorBase.__refs__:
            for ref in SelectorBase. __refs__:
                if ref == tmp:
                    return ref
        return tmp

    def __init__(self):
        SelectorBase.__refs__.add(self)

    def __eq__(self, other):
        if other is None:
            return False
        return repr(self) == repr(other)

    def __lt__(self, other):
        return repr(self) < repr(other)

    def __hash__(self):
        return self._hash #pylint: disable=no-member

    @abstractmethod
    def set_descriptions(self, *args, **kwargs):
        pass


class EqualitySelector(SelectorBase):
    def __init__(self, attribute_name, attribute_value, selector_name=None):
        if attribute_name is None:
            raise TypeError()
        if attribute_value is None:
            raise TypeError()
        self._attribute_name = attribute_name
        self._attribute_value = attribute_value
        self._selector_name = selector_name
        self.set_descriptions(self._attribute_name, self._attribute_value, self._selector_name)
        super().__init__()

    @property
    def attribute_name(self):
        return self._attribute_name

    @property
    def attribute_value(self):
        return self._attribute_value

    def set_descriptions(self, attribute_name, attribute_value, selector_name=None): # pylint: disable=arguments-differ
        self._hash, self._query, self._string = EqualitySelector.compute_descriptions(attribute_name, attribute_value, selector_name=selector_name)

    @classmethod
    def compute_descriptions(cls, attribute_name, attribute_value, selector_name):
        if isinstance(attribute_value, (str, bytes)):
            query = str(attribute_name) + "==" + "'" + str(attribute_value) + "'"
        elif np.isnan(attribute_value):
            query = attribute_name + ".isnull()"
        else:
            query = str(attribute_name) + "==" + str(attribute_value)
        if selector_name is not None:
            string_ = selector_name
        else:
            string_ = query
        hash_value = hash(query)
        return (hash_value, query, string_)

    def __repr__(self):
        return self._query

    def covers(self, data):
        row = data[self.attribute_name].to_numpy()
        if pd.isnull(self.attribute_value):
            return pd.isnull(row)
        return row == self.attribute_value

    def __str__(self, open_brackets="", closing_brackets=""):
        return open_brackets + self._string + closing_brackets

# Including the lower bound, excluding the upper_bound
class IntervalSelector(SelectorBase):
    def __init__(self, attribute_name, lower_bound, upper_bound, selector_name=None):
        self._attribute_name = attribute_name
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self.selector_name = selector_name
        self.set_descriptions(attribute_name, lower_bound, upper_bound, selector_name)
        super().__init__()

    @property
    def attribute_name(self):
        return self._attribute_name

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    def covers(self, data_instance):
        val = data_instance[self.attribute_name].to_numpy()
        return np.logical_and(val >= self.lower_bound, val < self.upper_bound)

    def __repr__(self):
        return self._query

    def __hash__(self):
        return self._hash

    def __str__(self):
        return self._string

    @classmethod
    def compute_descriptions(cls, attribute_name, lower_bound, upper_bound, selector_name=None):
        if selector_name is None:
            _string = cls.compute_string(attribute_name, lower_bound, upper_bound, rounding_digits=2)
        else:
            _string = selector_name
        _query = cls.compute_string(attribute_name, lower_bound, upper_bound, rounding_digits=None)
        _hash = _query.__hash__()
        return (_hash, _query, _string)

    def set_descriptions(self, attribute_name, lower_bound, upper_bound, selector_name=None):  # pylint: disable=arguments-differ
        self._hash, self._query, self._string = IntervalSelector.compute_descriptions(attribute_name, lower_bound, upper_bound, selector_name=selector_name)

    @classmethod
    def compute_string(cls, attribute_name, lower_bound, upper_bound, rounding_digits):
        if rounding_digits is None:
            formatter = "{}"
        else:
            formatter = "{0:." + str(rounding_digits) + "f}"
        ub = upper_bound
        lb = lower_bound
        if ub % 1:
            ub = formatter.format(ub)
        if lb % 1:
            lb = formatter.format(lb)

        if lower_bound == float("-inf") and upper_bound == float("inf"):
            repre = attribute_name + "= anything"
        elif lower_bound == float("-inf"):
            repre = attribute_name + "<" + str(ub)
        elif upper_bound == float("inf"):
            repre = attribute_name + ">=" + str(lb)
        else:
            repre = attribute_name + ": [" + str(lb) + ":" + str(ub) + "["
        return repre

@total_ordering
class BinaryTarget:

    def __init__(self, target_attribute=None, target_value=None, target_selector=None):
        """
        Creates a new target for the boolean model class (classic subgroup discovery).
        If target_attribute and target_value are given, the target_selector is computed using attribute and value
        """
        if target_attribute is not None and target_value is not None:
            if target_selector is not None:
                raise BaseException("BinaryTarget is to be constructed EITHER by a selector OR by attribute/value pair")
            target_selector = EqualitySelector(target_attribute, target_value)
        if target_selector is None:
            raise BaseException("No target selector given")
        self.target_selector = target_selector

    def __repr__(self):
        return "T: " + str(self.target_selector)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return str(self) < str(other)

    def covers(self, instance):
        return self.target_selector.covers(instance)

    def get_base_statistics(self, subgroup, data):

        sg_instances = subgroup.covers(data)
        positives = self.covers(data)
        instances_subgroup = np.sum(sg_instances)
        positives_dataset = np.sum(positives)
        instances_dataset = len(data)
        positives_subgroup = np.sum(np.logical_and(sg_instances, positives))
        return instances_dataset, positives_dataset, instances_subgroup, positives_subgroup

    def calculate_statistics(self, subgroup, data):
        (instances_dataset, positives_dataset, instances_subgroup, positives_subgroup) = \
            self.get_base_statistics(subgroup, data)
        statistics = {}
        statistics['size_sg'] = instances_subgroup
        statistics['size_dataset'] = instances_dataset
        statistics['positives_sg'] = positives_subgroup
        statistics['positives_dataset'] = positives_dataset
        statistics['size_complement'] = instances_dataset - instances_subgroup
        statistics['relative_size_sg'] = instances_subgroup / instances_dataset
        statistics['relative_size_complement'] = (instances_dataset - instances_subgroup) / instances_dataset
        statistics['coverage_sg'] = positives_subgroup / positives_dataset
        statistics['coverage_complement'] = (positives_dataset - positives_subgroup) / positives_dataset
        statistics['target_share_sg'] = positives_subgroup / instances_subgroup
        statistics['target_share_complement'] = (positives_dataset - positives_subgroup) / (
                instances_dataset - instances_subgroup)
        statistics['target_share_dataset'] = positives_dataset / instances_dataset
        statistics['lift'] = (positives_subgroup / instances_subgroup) / (positives_dataset / instances_dataset)
        return statistics

def create_selectors(data, nbins=5, intervals_only=True, ignore=None):
    if ignore is None:
        ignore = []
    sels = create_nominal_selectors(data, ignore)
    sels.extend(create_numeric_selectors(data, nbins, intervals_only, ignore=ignore))
    return sels

def create_nominal_selectors(data, ignore=None):
    if ignore is None:
        ignore = []
    nominal_selectors = []
    # for attr_name in [x for x in data.select_dtypes(exclude=['number']).columns.values if x not in ignore]:
    #    nominal_selectors.extend(create_nominal_selectors_for_attribute(data, attr_name))
    nominal_dtypes = data.select_dtypes(exclude=['number'])
    dtypes = data.dtypes
    # print(dtypes)
    for attr_name in [x for x in nominal_dtypes.columns.values if x not in ignore]:
        nominal_selectors.extend(create_nominal_selectors_for_attribute(data, attr_name, dtypes))
    return nominal_selectors

def create_nominal_selectors_for_attribute(data, attribute_name, dtypes=None):
    nominal_selectors = []
    for val in pd.unique(data[attribute_name]):
        nominal_selectors.append(EqualitySelector(attribute_name, val))
    # setting the is_bool flag for selector
    if dtypes is None:
        dtypes = data.dtypes
    if dtypes[attribute_name] == 'bool':
        for s in nominal_selectors:
            s.is_bool = True
    return nominal_selectors

def create_numeric_selectors(data, nbins=5, intervals_only=True, weighting_attribute=None, ignore=None):
    if ignore is None:
        ignore = []
    numeric_selectors = []
    for attr_name in [x for x in data.select_dtypes(include=['number']).columns.values if x not in ignore]:
        numeric_selectors.extend(create_numeric_selector_for_attribute(
            data, attr_name, nbins, intervals_only, weighting_attribute))
    return numeric_selectors

def create_numeric_selector_for_attribute(data, attr_name, nbins=5, intervals_only=True, weighting_attribute=None):
    numeric_selectors = []
    data_not_null = data[data[attr_name].notnull()]

    uniqueValues = np.unique(data_not_null[attr_name])
    if len(data_not_null.index) < len(data.index):
        numeric_selectors.append(EqualitySelector(attr_name, np.nan))

    if len(uniqueValues) <= nbins:
        for val in uniqueValues:
            numeric_selectors.append(EqualitySelector(attr_name, val))
    else:
        cutpoints = u.equal_frequency_discretization(data, attr_name, nbins, weighting_attribute)
        if intervals_only:
            old_cutpoint = float("-inf")
            for c in cutpoints:
                numeric_selectors.append(IntervalSelector(attr_name, old_cutpoint, c))
                old_cutpoint = c
            numeric_selectors.append(IntervalSelector(attr_name, old_cutpoint, float("inf")))
        else:
            for c in cutpoints:
                numeric_selectors.append(IntervalSelector(attr_name, c, float("inf")))
                numeric_selectors.append(IntervalSelector(attr_name, float("-inf"), c))

    return numeric_selectors
