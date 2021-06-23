from eth_keys.datatypes import PrivateKey
from eth_typing import Address

from eth.vm.forks.berlin.transactions import (
    BerlinLegacyTransaction,
    BerlinUnsignedLegacyTransaction,
)

from eth._utils.transactions import (
    create_transaction_signature,
)


class SimpleTransaction(BerlinLegacyTransaction):
    @classmethod
    def create_unsigned_transaction(cls,
                                    *,
                                    nonce: int,
                                    gas_price: int,
                                    gas: int,
                                    to: Address,
                                    value: int,
                                    data: bytes) -> 'SimpleUnsignedTransaction':
        return SimpleUnsignedTransaction(nonce, gas_price, gas, to, value, data)


class SimpleUnsignedTransaction(BerlinUnsignedLegacyTransaction):
    def as_signed_transaction(self,
                              private_key: PrivateKey,
                              chain_id: int = None) -> SimpleTransaction:
        v, r, s = create_transaction_signature(self, private_key, chain_id=chain_id)
        return SimpleTransaction(
            nonce=self.nonce,
            gas_price=self.gas_price,
            gas=self.gas,
            to=self.to,
            value=self.value,
            data=self.data,
            v=v,
            r=r,
            s=s,
        )
