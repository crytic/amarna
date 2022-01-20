func shared_state_serialize{output_ptr : felt*}(shared_state : SharedState*):
    alloc_locals
    local output_start_ptr : felt* = output_ptr
#     # Storing an empty slot for the size of the structure which will be filled later in the code.
#     # A single slot due to the implementation of serialize_word which increments the ptr by one.
#     let output_ptr = output_ptr + 1
#     serialize_word(shared_state.positions_root)
#     serialize_word(shared_state.positions_tree_height)
#     serialize_word(shared_state.orders_root)
#     serialize_word(shared_state.orders_tree_height)
#     funding_indices_info_serialize(shared_state.global_funding_indices)
#     let (callback_adddress) = get_label_location(label_value=oracle_price_serialize)
#     serialize_array(
#         array=shared_state.oracle_prices.data,
#         n_elms=shared_state.oracle_prices.len,
#         elm_size=OraclePrice.SIZE,
#         callback=callback_adddress)
#     serialize_word(shared_state.system_time)
#     let size = cast(output_ptr, felt) - cast(output_start_ptr, felt) - 1
    serialize_array(
        array=program_output.asset_configs,
        n_elms=program_output.n_asset_configs,
        elm_size=AssetConfigHashEntry.SIZE,
        callback=asset_config_hash_serialize + __pc__ - ret_pc_label)
    serialize_word{output_ptr=output_start_ptr}(size)
    return ()
end

