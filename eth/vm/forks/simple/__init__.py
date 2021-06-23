from typing import (
    Type,
)

from eth.rlp.blocks import BaseBlock
from eth.vm.forks.berlin import (
    BerlinVM,
)
from eth.vm.state import BaseState

from .blocks import SimpleBlock
from .headers import (
    compute_simple_difficulty,
    configure_simple_header,
    create_simple_header_from_parent,
)
from .state import SimpleState


class SimpleVM(BerlinVM):
    # fork name
    fork = 'simple'
    # classes
    block_class: Type[BaseBlock] = SimpleBlock
    _state_class: Type[BaseState] = SimpleState

    # Methods
    create_header_from_parent = staticmethod(create_simple_header_from_parent)  # type: ignore
    compute_difficulty = staticmethod(compute_simple_difficulty)    # type: ignore
    configure_header = configure_simple_header