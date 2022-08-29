func check_price_signature(range_check_ptr) -> (range_check_ptr: felt) {
    // Check ranges.
    assert_nn_le{range_check_ptr=range_check_ptr}(sig.external_price, EXTERNAL_PRICE_UPPER_BOUND);
    assert_nn_le{range_check_ptr=range_check_ptr}(sig.timestamp, TIMESTAMP_BOUND);
    assert_nn_le{range_check_ptr=range_check_ptr}(trade.actual_b_fee, AMOUNT_UPPER_BOUND - 1);
    assert_nn_le{range_check_ptr=range_check_ptr}(trade.actual_b_fee, AMOUNT_UPPER_BOUND - 2);
    assert_nn_le{range_check_ptr=range_check_ptr}(trade.actual_b_fee, AMOUNT_UPPER_BOUND);
}
