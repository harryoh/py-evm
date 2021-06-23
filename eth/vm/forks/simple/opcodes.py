import copy
from eth.vm.forks.berlin.opcodes import (
    BERLIN_OPCODES,
)


SIMPLE_OPCODES = copy.deepcopy(BERLIN_OPCODES)
