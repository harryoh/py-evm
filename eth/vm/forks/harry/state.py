from eth_hash.auto import keccak
from eth_typing import Address
from eth_utils import (
    encode_hex,
)

from eth.validation import (
    validate_is_bytes,
    validate_uint256,
    validate_canonical_address,
)

from eth.abc import (
    ComputationAPI,
    SignedTransactionAPI,
    MessageAPI,
)
from eth.constants import CREATE_CONTRACT_ADDRESS
from eth.exceptions import (
    ContractCreationCollision,
)

from eth._utils.address import (
    generate_contract_address,
)

from eth.vm.message import (
    Message,
)
from eth.vm.forks.frontier.state import (
    FrontierState,
    FrontierTransactionExecutor,
)

from .computation import HarryComputation
from .constants import (
    REFUND_SELFDESTRUCT,
    FEE_TOKEN
)

'''
    def set_balance(self, address: Address, balance: int) -> None:
        validate_canonical_address(address, title="Storage Address")
        validate_uint256(balance, title="Account Balance")

        account = self._get_account(address)
        self._set_account(address, account.copy(balance=balance))
'''

class HarryTransactionExecutor(FrontierTransactionExecutor):
    def get_fee_storage_pos(self, address: Address):
        return int.from_bytes(keccak((b"\0"*12 + address) + (b"\0"*31 + b"\1")), byteorder='big')

    def fee_delta_balance(self, sender: Address, delta: int):
        validate_canonical_address(sender, title="Storage Address")
        balance = self.vm_state.get_storage(Address(FEE_TOKEN), self.get_fee_storage_pos(sender)) + delta
        validate_uint256(balance, title="Account Balance")

        self.vm_state.set_storage(Address(FEE_TOKEN), self.get_fee_storage_pos(sender), balance)


    def build_evm_message(self, transaction: SignedTransactionAPI) -> MessageAPI:

        gas_fee = transaction.gas * transaction.gas_price

        # Buy Gas
        # self.vm_state.delta_balance(transaction.sender, -1 * gas_fee)

        self.fee_delta_balance(transaction.sender, -1 * gas_fee)

        # Increment Nonce
        self.vm_state.increment_nonce(transaction.sender)

        # Setup VM Message
        message_gas = transaction.gas - transaction.intrinsic_gas

        if transaction.to == CREATE_CONTRACT_ADDRESS:
            contract_address = generate_contract_address(
                transaction.sender,
                self.vm_state.get_nonce(transaction.sender) - 1,
            )
            data = b''
            code = transaction.data
        else:
            contract_address = None
            data = transaction.data
            code = self.vm_state.get_code(transaction.to)

        self.vm_state.logger.debug2(
            (
                "TRANSACTION: sender: %s | to: %s | value: %s | gas: %s | "
                "gas-price: %s | s: %s | r: %s | y_parity: %s | data-hash: %s"
            ),
            encode_hex(transaction.sender),
            encode_hex(transaction.to),
            transaction.value,
            transaction.gas,
            transaction.gas_price,
            transaction.s,
            transaction.r,
            transaction.y_parity,
            encode_hex(keccak(transaction.data)),
        )

        message = Message(
            gas=message_gas,
            to=transaction.to,
            sender=transaction.sender,
            value=transaction.value,
            data=data,
            code=code,
            create_address=contract_address,
        )
        return message

    def finalize_computation(self,
                             transaction: SignedTransactionAPI,
                             computation: ComputationAPI) -> ComputationAPI:
        # Self Destruct Refunds
        num_deletions = len(computation.get_accounts_for_deletion())
        if num_deletions:
            computation.refund_gas(REFUND_SELFDESTRUCT * num_deletions)

        # Gas Refunds
        gas_remaining = computation.get_gas_remaining()
        gas_refunded = computation.get_gas_refund()
        gas_used = transaction.gas - gas_remaining
        gas_refund = min(gas_refunded, gas_used // 2)
        gas_refund_amount = (gas_refund + gas_remaining) * transaction.gas_price

        if gas_refund_amount:
            self.vm_state.logger.debug2(
                'TRANSACTION REFUND: %s -> %s',
                gas_refund_amount,
                encode_hex(computation.msg.sender),
            )

            # self.vm_state.delta_balance(computation.msg.sender, gas_refund_amount)
            self.fee_delta_balance(computation.msg.sender, gas_refund_amount)

        # Miner Fees
        transaction_fee = \
            (transaction.gas - gas_remaining - gas_refund) * transaction.gas_price
        transaction_fee = 0
        self.vm_state.logger.debug2(
            'TRANSACTION FEE: %s -> %s',
            transaction_fee,
            encode_hex(self.vm_state.coinbase),
        )
        # self.vm_state.delta_balance(self.vm_state.coinbase, transaction_fee)
        self.fee_delta_balance(self.vm_state.coinbase, transaction_fee)

        # Process Self Destructs
        for account, _ in computation.get_accounts_for_deletion():
            # TODO: need to figure out how we prevent multiple selfdestructs from
            # the same account and if this is the right place to put this.
            self.vm_state.logger.debug2('DELETING ACCOUNT: %s', encode_hex(account))

            # TODO: this balance setting is likely superflous and can be
            # removed since `delete_account` does this.
            self.vm_state.set_balance(account, 0)
            self.vm_state.delete_account(account)

        return computation

class HarryState(FrontierState):
    computation_class = HarryComputation
    transaction_executor_class = HarryTransactionExecutor
