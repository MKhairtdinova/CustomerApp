from SubgroupDiscovery.QualityFunctions import base_qual as bq
import scipy.stats
from SubgroupDiscovery import utils as u
from SubgroupDiscovery.QualityFunctions import qual_interface as iqual
import zope.interface


@zope.interface.implementer(iqual.IQuality)
class ChiSquaredQF(bq.SimplePositivesQF):
    """
    ChiSquaredQF which test for statistical independence of a subgroup against it's complement
    ...
    """

    qual_name = 'Хи-квадрат'

    values_restrict = {'direction': ['both', 'positive', 'negative'], 'stat': ['chi2', 'p']}

    @staticmethod
    def chi_squared_qf(instances_dataset, positives_dataset, instances_subgroup, positives_subgroup, min_instances=5,
                       bidirect=True, direction_positive=True, index=0):
        """
        Performs chi2 test of statistical independence
        Test whether a subgroup is statistically independent from it's complement (see scipy.stats.chi2_contingency).
        Parameters
        ----------
        instances_dataset, positives_dataset, instances_subgroup, positives_subgroup : int
            counts of subgroup and dataset
        min_instances : int, optional
            number of required instances, if less -inf is returned for that subgroup
        bidirect : bool, optional
            If true both directions are considered interesting else direction_positive decides which direction is interesting
        direction_positive: bool, optional
            Only used if bidirect=False; specifies whether you are interested in positive (True) or negative deviations
        index : {0, 1}, optional
            decides whether the test statistic (0) or the p-value (1) should be used
        """

        if (instances_subgroup < min_instances) or ((instances_dataset - instances_subgroup) < min_instances):
            return float("-inf")

        negatives_subgroup = instances_subgroup - positives_subgroup  # pylint: disable=bad-whitespace
        negatives_dataset = instances_dataset - positives_dataset  # pylint: disable=bad-whitespace
        negatives_complement = negatives_dataset - negatives_subgroup
        positives_complement = positives_dataset - positives_subgroup

        val = scipy.stats.chi2_contingency([[positives_subgroup, positives_complement],
                                            [negatives_subgroup, negatives_complement]], correction=False)[index]
        if bidirect:
            return val
        p_subgroup = positives_subgroup / instances_subgroup
        p_dataset = positives_dataset / instances_dataset
        if direction_positive and p_subgroup > p_dataset:
            return val
        elif not direction_positive and p_subgroup < p_dataset:
            return val
        return -val

    @staticmethod
    def chi_squared_qf_weighted(subgroup, data, weighting_attribute, effective_sample_size=0, min_instances=5, ):
        (instancesDataset, positivesDataset, instancesSubgroup, positivesSubgroup) = subgroup.get_base_statistics(data,
                                                                                                                  weighting_attribute)
        if (instancesSubgroup < min_instances) or ((instancesDataset - instancesSubgroup) < 5):
            return float("inf")
        if effective_sample_size == 0:
            effective_sample_size = u.effective_sample_size(data[weighting_attribute])
        # p_subgroup = positivesSubgroup / instancesSubgroup
        # p_dataset = positivesDataset / instancesDataset

        negatives_subgroup = instancesSubgroup - positivesSubgroup
        negatives_dataset = instancesDataset - positivesDataset
        positives_complement = positivesDataset - positivesSubgroup
        negatives_complement = negatives_dataset - negatives_subgroup
        val = scipy.stats.chi2_contingency([[positivesSubgroup, positives_complement],
                                            [negatives_subgroup, negatives_complement]], correction=True)[0]
        return scipy.stats.chi2.sf(val * effective_sample_size / instancesDataset, 1)

    def __init__(self, direction: str = 'both', min_instances: int = 5, stat: str = 'chi2'):
        """
        Parameters
        ----------
        direction : {'both', 'positive', 'negative'}
            direction of deviation that is of interest
        min_instances : int, optional
            number of required instances, if less -inf is returned for that subgroup
        stat : {'chi2', 'p'}
            whether to report the test statistic or the p-value (see scipy.stats.chi2_contingency)
        """

        if direction == 'both':
            self.bidirect = True
            self.direction_positive = True
        if direction == 'positive':
            self.bidirect = False
            self.direction_positive = True
        if direction == 'negative':
            self.bidirect = False
            self.direction_positive = False
        self.min_instances = min_instances
        self.index = {'chi2': 0, 'p': 1}[stat]
        super().__init__()

    def evaluate(self, subgroup, statistics=None):
        statistics = self.ensure_statistics(subgroup, statistics)
        datatset = self.datatset_statistics
        return ChiSquaredQF.chi_squared_qf(datatset.size, datatset.positives_count, statistics.size,
                                           statistics.positives_count, self.min_instances, self.bidirect,
                                           self.direction_positive, self.index)

    def supports_weights(self):
        return True
