from eth.vm.forks.berlin.state import (
    BerlinState
)

from .computation import SimpleComputation


class SimpleState(BerlinState):
    computation_class = SimpleComputation
