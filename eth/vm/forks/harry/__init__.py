from typing import (
    Type,
)

from eth.abc import (
    BlockAPI,
    StateAPI,
)

from eth.rlp.blocks import BaseBlock
from eth.vm.forks.frontier import (
    FrontierVM,
)

from .blocks import HarryBlock
from .headers import (
    compute_harry_difficulty,
    configure_harry_header,
    create_harry_header_from_parent,
)
from .state import HarryState


class HarryVM(FrontierVM):
    # fork name
    fork = 'harry'
    # classes
    block_class: Type[BlockAPI] = HarryBlock
    _state_class: Type[BlockAPI] = HarryState

    # Methods
    create_header_from_parent = staticmethod(create_harry_header_from_parent)  # type: ignore
    compute_difficulty = staticmethod(compute_harry_difficulty)    # type: ignore
    configure_header = configure_harry_header
