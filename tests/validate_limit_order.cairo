from services.perpetual.cairo.definitions.perpetual_error_code import PerpetualErrorCode
from services.perpetual.cairo.order.limit_order import LimitOrder
from starkware.cairo.common.cairo_builtins import HashBuiltin as hashstuff, ASD as rewwerw
from starkware.cairo.common.math import assert_le, assert_lt, assert_nn

# Validates limit order fulfillment.
# Asserts that the actual amounts are fair with respect to the signed limit order.
#
# Checks that the party will not lose on the ratio between buying and selling and will not be
# charged more fee, with respect to the collateral, than was signed on in the order.
# I.e.,
#    actual_fee / actual_collaterall <= amount_fee / amount_collateral
#    actual_sold / actual_bought <= amount_sell / amount_buy (with the relaxation below).
#
# We relax the inequality, to allow rounding of actual_collateral to either side.
# This allows to always produce valid actual_amounts for opposing orders,
# even when the amounts are very small.
#
# Assumption:
#   1 <= actual_synthetic <= order.amount_synthetic < AMOUNT_UPPER_BOUND
#   0 <= actual_collateral < AMOUNT_UPPER_BOUND
#   0 <= actual_fee < AMOUNT_UPPER_BOUND
#   0 <= order.amount_collateral < AMOUNT_UPPER_BOUND
#   0 <= order.amount_fee < AMOUNT_UPPER_BOUND
#   AMOUNT_UPPER_BOUND**2 <= rc_bound.
func validate_limit_order_fairness(
        range_check_ptr, limit_order : LimitOrder*, actual_collateral, actual_synthetic,
        actual_fee) -> (range_check_ptr):
    tempvar amount_collateral = limit_order.amount_collateral

    # The party won't be charged more fee, with respect to the synthetic asset, than was signed on
    # in the limit_order:
    # actual_fee / actual_collateral <= amount_fee / amount_collateral, thus
    # actual_fee * amount_collateral <= amount_fee * actual_collateral.
    %{ error_code = ids.PerpetualErrorCode.INVALID_FULFILLMENT_FEE_RATIO %}
    assert_le{range_check_ptr=range_check_ptr}(
        actual_fee * amount_collateral, limit_order.amount_fee * actual_collateral)
    %{ del error_code %}

    if limit_order.is_buying_synthetic != 0:
        # Buying synthetic.
        let actual_sold = actual_collateral
        let actual_bought = actual_synthetic
        let amount_sell = amount_collateral
        let amount_buy = limit_order.amount_synthetic

        if actual_sold == 0:
            # The buyer is always willing to get a synthetic for free.
            return (range_check_ptr=range_check_ptr)
        end

        # Since we sell collateral, we round actual_sold.
        # (actual_sold - 1) / actual_bought < amount_sell / amount_buy, thus
        # (actual_sold - 1) * amount_buy < amount_sell * actual_bought.
        %{ error_code = ids.PerpetualErrorCode.INVALID_FULFILLMENT_ASSETS_RATIO %}
        assert_lt{range_check_ptr=range_check_ptr}(
            (actual_sold - 1) * amount_buy, amount_sell * actual_bought)
        %{ del error_code %}
        return (range_check_ptr=range_check_ptr)
    end

    # Selling synthetic.
    let actual_sold = actual_synthetic
    let actual_bought = actual_collateral
    let amount_sell = limit_order.amount_synthetic
    let amount_buy = amount_collateral
    # Since we buy collateral, we round actual_bought.
    # actual_sold / (actual_bought + 1) < amount_sell / amount_buy, thus
    # actual_sold * amount_buy < amount_sell * (actual_bought + 1).
    %{ error_code = ids.PerpetualErrorCode.INVALID_FULFILLMENT_ASSETS_RATIO %}
    assert_lt{range_check_ptr=range_check_ptr}(
        actual_sold * amount_buy, amount_sell * (actual_bought + 1))
    %{ del error_code %}
    return (range_check_ptr=range_check_ptr)
end


func some_function(bar, foo) -> (range_check_ptr):
    return (range_check_ptr=bar)
end


func execute{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr,
        ecdsa_ptr: SignatureBuiltin*
    }(
        to: felt,
        selector: felt,
        calldata_len: felt,
        calldata: felt*,
        nonce: felt
    ) -> (response_len: felt, response: felt*):
    alloc_locals

    let (__fp__, _) = get_fp_and_pc()
    let (_address) = get_contract_address()
    let (_current_nonce) = current_nonce.read()


    local message: Message = Message(
        _address,
        to,
        selector,
        calldata,
        calldata_size=calldata_len,
        _current_nonce
    )

    # validate transaction
    let (hash) = hash_message(&message)
    let (signature_len, signature) = get_tx_signature()
    is_valid_signature(hash, signature_len, signature)

    # bump nonce
    current_nonce.write(_current_nonce + 1)

    # execute call
    let response = call_contract(
        contract_address=message.to,
        function_selector=message.selector,
        calldata_size=message.calldata_size,
        calldata=message.calldata
    )

    return (response_len=response.retdata_size, response=response.retdata)
end
