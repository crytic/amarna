func ERC721_transferFrom{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    }(_from: felt, to: felt, token_id: Uint256):
    let (caller) = get_caller_address()
    let (is_approved) = _is_approved_or_owner(caller, token_id)
    assert is_approved = 1

    _transfer(_from, to, token_id)
    return ()
end

func main():
    ERC721_transferFrom()
    return ()

end
