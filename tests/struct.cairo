struct Transfer:
    member base : OrderBase*
    member nonce : felt
    # sender_public_key is the base's public_key.
    member sender_position_id : felt
    member receiver_public_key : felt
    member receiver_position_id : felt
    member amount : felt
    member asset_id : felt
    member expiration_timestamp : felt
end

