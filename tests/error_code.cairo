func _safe_transfer{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    from_: felt, to: felt, token_id: Uint256, data_len: felt, data: felt*
) {
    _transfer(from_, to, token_id);
    let (success) = _check_onERC721Received(from_, to, token_id, data_len, data);
    with_attr error_message("ERC721: transfer to non ERC721Receiver implementer") {
        assert_not_zero(success);
    }
    return ();
}
