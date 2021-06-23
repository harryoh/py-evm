from rlp.sedes import (
    CountableList,
)
from eth.rlp.headers import (
    BlockHeader,
)
from eth.vm.forks.frontier.blocks import (
    FrontierBlock,
)

from .transactions import (
    HarryTransaction,
)


class HarryBlock(FrontierBlock):
    transaction_builder = HarryTransaction
    fields = [
        ('header', BlockHeader),
        ('transactions', CountableList(transaction_builder)),
        ('uncles', CountableList(BlockHeader))
    ]
