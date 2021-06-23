from eth.vm.forks.berlin.state import (
    BerlinState
)

from .computation import HarryComputation


class HarryState(BerlinState):
    computation_class = HarryComputation
