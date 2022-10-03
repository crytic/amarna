func update_position_in_dict(range_check_ptr) -> (range_check_ptr: felt) {
    local initial_position: Position*;
    local not_used: Position*;
    alloc_locals;

    %{ ids.initial_position = __dict_manager.get_dict(ids.positions_dict)[ids.position_id] %}

    let (range_check_ptr, updated_position, funded_position, return_code) = update_position(
        range_check_ptr=range_check_ptr, position=initial_position
    );

    // Even if update failed, we need to write the update.
    dict_update{dict_ptr=positions_dict}(
        key=position_id,
        prev_value=cast(initial_position, felt),
        new_value=cast(updated_position, felt),
    );
    initial_position = 3;
    return (
        range_check_ptr=range_check_ptr,
        positions_dict=positions_dict,
        funded_position=funded_position,
        updated_position=updated_position,
        return_code=return_code,
    );
}
