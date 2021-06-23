from typing import Type

from rlp.sedes import (
    CountableList,
)

from eth.abc import (
    ReceiptBuilderAPI,
    TransactionBuilderAPI,
)
from eth.rlp.headers import (
    BlockHeader,
)
from eth.vm.forks.berlin.blocks import (
    BerlinBlock,
)

from .receipts import (
    SimpleReceiptBuilder,
)
from .transactions import (
    SimpleTransactionBuilder,
)


class SimpleBlock(BerlinBlock):
    transaction_builder: Type[TransactionBuilderAPI] = SimpleTransactionBuilder  # type: ignore
    receipt_builder: Type[ReceiptBuilderAPI] = SimpleReceiptBuilder  # type: ignore
    fields = [
        ('header', BlockHeader),
        ('transactions', CountableList(transaction_builder)),
        ('uncles', CountableList(BlockHeader))
    ]
