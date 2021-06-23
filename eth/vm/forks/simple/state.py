from typing import Type

from eth.abc import (
    ComputationAPI,
    MessageAPI,
    SignedTransactionAPI,
    TransactionExecutorAPI,
)
from eth.vm.forks.berlin.state import (
    BerlinState
)
from eth.vm.forks.spurious_dragon.state import (
    SpuriousDragonTransactionExecutor,
)

from .computation import SimpleComputation


class SimpleTransactionExecutor(SpuriousDragonTransactionExecutor):
    def build_computation(
            self,
            message: MessageAPI,
            transaction: SignedTransactionAPI) -> ComputationAPI:

        self.vm_state.mark_address_warm(transaction.sender)

        # Mark recipient as accessed, or the new contract being created
        self.vm_state.mark_address_warm(message.storage_address)

        for address, slots in transaction.access_list:
            self.vm_state.mark_address_warm(address)
            for slot in slots:
                self.vm_state.mark_storage_warm(address, slot)

        return super().build_computation(message, transaction)


class SimpleState(BerlinState):
    computation_class = SimpleComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = SimpleTransactionExecutor
