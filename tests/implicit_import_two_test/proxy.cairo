%lang starknet

from utils import auth_read_storage

// Allow owner to read all the contract's state
@view
func read_state{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(address: felt) -> (
    value: felt
) {
    let (owner_account) = owner.read();
    let (value) = auth_read_storage(owner_account, address);
    return (value,);
}
