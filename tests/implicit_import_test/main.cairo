# main.cairo

from library import mint_internal, assert_owner

@external
func mint(to : felt, amount : felt):
    assert_owner()
    mint_internal(to, amount)
    return ()
end
