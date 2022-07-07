# Adds two integers. 
# Reverts if the sum overflows.
func add{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (a: Uint256, b: Uint256) -> (c: Uint256):
    uint256_check(a)
    uint256_check(b)
    let (c: Uint256, is_overflow) = uint256_add(a, b)
    with_attr error_message("SafeUint256: addition overflow"):
        assert is_overflow = FALSE
    end
    return (c)
end

# Adds two integers. 
# Reverts if the sum overflows.
func add{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (a: Uint256, b: Uint256) -> (c: Uint256):
    uint256_check(a)
    uint256_check(b)
    let (c: Uint256, _) = uint256_add(a, b)
    return (c)
end