// library.cairo

func assert_owner() {
    let (caller) = get_caller_address();
    let (owner) = owner_storage.read();
    assert caller = owner;
    return ();
}

func mint_internal(to: felt, amount: felt) {
    let (balance) = balance_of.read(to);
    balance_of.write(to, balance + amount);
    return ();
}

@external
func test_mint(to, amount) {
    mint_internal(to, amount);
    return ();
}

@view
func test2() {
    return ();
}

@l1_handler
func test3() {
    return ();
}
