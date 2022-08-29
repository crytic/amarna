%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from a import a_get_balance, a_increase_balance
from b import b_get_balance, b_increase_balance

@external
func increase_balance_a{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    a_increase_balance(amount);
    return ();
}

@external
func increase_balance_b{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    b_increase_balance(amount);
    return ();
}

@view
func get_balance_a{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    res: felt
) {
    let (res) = a_get_balance();
    return (res,);
}

@view
func get_balance_b{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    res: felt
) {
    let (res) = b_get_balance();
    return (res,);
}
