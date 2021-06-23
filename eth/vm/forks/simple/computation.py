from eth.vm.forks.berlin.computation import (
    BERLIN_PRECOMPILES
)
from eth.vm.forks.berlin.computation import (
    BerlinComputation,
)

from .opcodes import SIMPLE_OPCODES

SIMPLE_PRECOMPILES = BERLIN_PRECOMPILES


class SimpleComputation(BerlinComputation):
    """
    A class for all execution computations in the ``Simple`` fork.
    Inherits from :class:`~eth.vm.forks.constantinople.berlin.BerlinComputation`
    """
    # Override
    opcodes = SIMPLE_OPCODES
    _precompiles = SIMPLE_PRECOMPILES
