struct Transfer {
    base: OrderBase*,
    nonce: felt,
    // sender_public_key is the base's public_key.
    sender_position_id: felt,
    receiver_public_key: felt,
    receiver_position_id: felt,
    amount: felt,
    asset_id: felt,
    expiration_timestamp: felt,
}
