func shared_state_serialize{output_ptr : felt*}(shared_state : SharedState*):
    alloc_locals
    local output_start_ptr : felt* = output_ptr
    serialize_array(
        array=program_output.asset_configs,
        n_elms=program_output.n_asset_configs,
        elm_size=AssetConfigHashEntry.SIZE,
        callback=asset_config_hash_serialize + __pc__ - ret_pc_label)
    serialize_word{output_ptr=output_start_ptr}(size)
    return ()
end

