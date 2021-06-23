from eth.vm.forks.frontier.computation import (
    FRONTIER_PRECOMPILES
)
from eth.vm.forks.frontier.computation import (
    FrontierComputation,
)

from .opcodes import HARRY_OPCODES

HARRY_PRECOMPILES = FRONTIER_PRECOMPILES


class HarryComputation(FrontierComputation):
    """
    A class for all execution computations in the ``Harry`` fork.
    Inherits from :class:`~eth.vm.forks.constantinople.frontier.FrontierComputation`
    """
    # Override
    opcodes = HARRY_OPCODES
    _precompiles = HARRY_PRECOMPILES
