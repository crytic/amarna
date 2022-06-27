@view
func bad_get_nonce{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (nonce : felt):
    let (user) = get_caller_address()
    let (nonce) = user_nonces.read(user)
    user_nonces.write(user, nonce + 1)

    return (nonce)
end