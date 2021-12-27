
from lark import Lark

with open('json.lark', 'r') as f:
    lark_spec = f.read()

json_parser = Lark(lark_spec, start='value')

text = '{"key": ["item0", "item1", 3.14]}'
t = json_parser.parse(text)



with open('cairo.lark', 'r') as f:
    lark_spec = f.read()

cairo_parser = Lark(lark_spec, start='cairo')

text = '''# 0 <= amount, max_amount_fee < AMOUNT_UPPER_BOUND
# 0 <= expiration_timestamp < EXPIRATION_TIMESTAMP_UPPER_BOUND.
func transfer_hash{pedersen_ptr : HashBuiltin*}(transfer : ExchangeTransfer*, condition : felt) -> (transfer_hash):
    alloc_locals
    const TRANSFER_ORDER_TYPE = 4
    const CONDITIONAL_TRANSFER_ORDER_TYPE = 5
    let (msg) = hash2{hash_ptr=pedersen_ptr}(x=transfer.asset_id, y=transfer.asset_id_fee)
    let (msg) = hash2{hash_ptr=pedersen_ptr}(x=msg, y=transfer.receiver_public_key)

    # The sender is the one that pays the fee.
    let src_fee_vault_id = transfer.sender_vault_id
    let packed_message0 = transfer.sender_vault_id
    let packed_message0 = packed_message0 * VAULT_ID_UPPER_BOUND + transfer.receiver_vault_id
    let packed_message0 = packed_message0 * VAULT_ID_UPPER_BOUND + src_fee_vault_id
    let packed_message0 = packed_message0 * NONCE_UPPER_BOUND + transfer.base.nonce
end'''

t = cairo_parser.parse(text)



print(t.pretty())