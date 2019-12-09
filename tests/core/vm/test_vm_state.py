import pytest

from eth_utils import ValidationError

from eth.tools.factories.transaction import (
    new_transaction
)
from eth.vm.interrupt import MissingAccountTrieNode


ADDRESS = b'\xaa' * 20
OTHER_ADDRESS = b'\xbb' * 20
INVALID_ADDRESS = b'aa' * 20


@pytest.fixture
def state(chain_without_block_validation):
    return chain_without_block_validation.get_vm().state


def test_block_properties(chain_without_block_validation):
    chain = chain_without_block_validation
    vm = chain.get_vm()
    block, _, _ = chain.import_block(vm.mine_block())

    assert vm.state.coinbase == block.header.coinbase
    assert vm.state.timestamp == block.header.timestamp
    assert vm.state.block_number == block.header.block_number
    assert vm.state.difficulty == block.header.difficulty
    assert vm.state.gas_limit == block.header.gas_limit


def test_missing_state_root(chain_without_block_validation, funded_address):
    valid_vm = chain_without_block_validation.get_vm()
    tx = new_transaction(valid_vm, from_=funded_address, to=ADDRESS)

    head = chain_without_block_validation.get_canonical_head()
    header_with_bad_state_root = head.copy(state_root=b'X' * 32)
    busted_vm = chain_without_block_validation.get_vm(header_with_bad_state_root)

    # notice that the state root is missing by the raised MissingAccountTrieNode
    with pytest.raises(MissingAccountTrieNode):
        busted_vm.state.apply_transaction(tx)


@pytest.mark.parametrize(
    'address, slot',
    (
        (INVALID_ADDRESS, 0),
        (ADDRESS, b'\0'),
        (ADDRESS, None),
    ),
)
def test_get_storage_input_validation(state, address, slot):
    with pytest.raises(ValidationError):
        state.get_storage(address, slot)


@pytest.mark.parametrize(
    'address, slot, new_value',
    (
        (INVALID_ADDRESS, 0, 0),
        (ADDRESS, b'\0', 0),
        (ADDRESS, 0, b'\0'),
        (ADDRESS, 0, None),
        (ADDRESS, None, 0),
    ),
)
def test_set_storage_input_validation(state, address, slot, new_value):
    with pytest.raises(ValidationError):
        state.set_storage(address, slot, new_value)


def test_delete_storage_input_validation(state):
    with pytest.raises(ValidationError):
        state.delete_storage(INVALID_ADDRESS)


@pytest.mark.parametrize('read_storage_before_snapshot', [True, False])
def test_revert_selfdestruct(state, read_storage_before_snapshot):
    state.set_storage(ADDRESS, 1, 2)
    state.persist()

    if read_storage_before_snapshot:
        assert state.get_storage(ADDRESS, 1) == 2

    # take a snapshot when the ADDRESS storage is *not* dirty, so it doesn't have a checkpoint
    snapshot = state.snapshot()

    # simulate a self-destruct, which puts a clear() in the storage journal
    state.delete_account(ADDRESS)

    # revert *all* changes to journal, aka pop_all()
    state.revert(snapshot)

    # This was breaking (returning storage value = 0) in two different scenarios:
    # - when there is a storage read before snapshot, because the journal
    #       forgot to set _ignore_wrapped_db = False on a complete journal reset
    # - when there is *not* a storage read before snapshot, because the storage
    #       would be loaded for the first time after the account was deleted, so the
    #       "starting" storage root hash would always be the empty one, which causes
    #       it to not be able to recover from a revert
    assert state.get_storage(ADDRESS, 1) == 2


def test_lock_state(state):
    assert state.get_storage(ADDRESS, 1, from_journal=False) == 0

    state.set_storage(ADDRESS, 1, 2)
    assert state.get_storage(ADDRESS, 1, from_journal=False) == 0

    state.lock_changes()
    assert state.get_storage(ADDRESS, 1, from_journal=False) == 2
