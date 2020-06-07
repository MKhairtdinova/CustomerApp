from SubgroupDiscovery import subgroup_task as st
from SubgroupDiscovery import utils as u
from SubgroupDiscovery import boolean_expressions as bexp
from SubgroupDiscovery.Algorythms import alg_interface as ialg

import zope.interface


@zope.interface.implementer(ialg.IAlgorithm)
class BeamSearch:
    '''
    Implements the BeamSearch algorithm. Its a basic implementation
    '''
    alg_name = 'Beam Search'
    values_restrict = dict()

    def __init__(self, beam_width: int = 20, beam_width_adaptive: bool = False):
        self.beam_width = beam_width
        self.beam_width_adaptive = beam_width_adaptive

    def execute(self, task):
        # adapt beam width to the result set size if desired
        if self.beam_width_adaptive:
            self.beam_width = task.result_set_size

        # check if beam size is to small for result set
        if self.beam_width < task.result_set_size:
            raise RuntimeError('Beam width in the beam search algorithm is smaller than the result set size!')

        task.qf.calculate_constant_statistics(task)

        # init
        beam = [(0, bexp.Conjunction([]))]
        last_beam = None

        depth = 0
        while beam != last_beam and depth < task.depth:
            last_beam = beam.copy()
            for (_, last_sg) in last_beam:
                if not getattr(last_sg, 'visited', False):
                    setattr(last_sg, 'visited', True)
                    for sel in task.search_space:
                        # create a clone
                        new_selectors = list(last_sg._selectors)
                        if sel not in new_selectors:
                            new_selectors.append(sel)
                            sg = bexp.Conjunction(new_selectors)
                            quality = task.qf.evaluate(sg, task.data)
                            u.add_if_required(beam, sg, quality, task, check_for_duplicates=True)
            depth += 1

        result = beam[:task.result_set_size]
        result.sort(key=lambda x: x[0], reverse=True)
        return st.SubgroupDiscoveryResult(result, task)
